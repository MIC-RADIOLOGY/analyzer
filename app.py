import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Accounts Receivable Aging Analyzer")

st.write("Upload an aging report to analyze receivables.")

uploaded_file = st.file_uploader(
    "Upload Aging Report",
    type=["xlsx","csv"]
)

if uploaded_file:

    if uploaded_file.name.endswith("xlsx"):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)

    st.subheader("Uploaded Data")
    st.dataframe(df)

    provider = "Provider"
    balance = "Balance"
    current = "Current"
    days30 = "30 Days"
    days60 = "60 Days"
    days90 = "90 Days"
    days120 = "120 Days"
    days150 = "150 Days"
    days180 = "180 Days Plus"
    unallocated = "Unallocated"

    total_ar = df[balance].sum()
    current_total = df[current].sum()

    d30 = df[days30].sum()
    d60 = df[days60].sum()
    d90 = df[days90].sum()
    d120 = df[days120].sum()
    d150 = df[days150].sum()
    d180 = df[days180].sum()

    unallocated_total = df[unallocated].sum()

    overdue = total_ar - current_total
    adjusted_receivables = total_ar - abs(unallocated_total)
    overdue_percent = overdue / total_ar * 100
    high_risk = d90 + d120 + d150 + d180
    bad_debt = d120 + d150 + d180

    st.subheader("Key Financial Metrics")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Receivables", f"${total_ar:,.0f}")
    col2.metric("Adjusted Receivables", f"${adjusted_receivables:,.0f}")
    col3.metric("Overdue", f"${overdue:,.0f}")
    col4.metric("Overdue %", f"{overdue_percent:.1f}%")

    aging_data = pd.DataFrame({
        "Bucket":["180+","150","120","90","60","30","Current"],
        "Amount":[d180,d150,d120,d90,d60,d30,current_total]
    })

    fig = px.bar(
        aging_data,
        x="Bucket",
        y="Amount",
        title="Accounts Receivable Aging Distribution"
    )

    st.plotly_chart(fig)

    st.subheader("Top Debtors")

    top_debtors = df.sort_values(
        balance,
        ascending=False
    ).head(10)

    fig2 = px.bar(
        top_debtors,
        x=provider,
        y=balance,
        title="Top 10 Debtors"
    )

    st.plotly_chart(fig2)

    st.subheader("Credit Balances")

    credit = df[df[unallocated] < 0]

    st.dataframe(credit[[provider, unallocated]])

    st.subheader("Management Insights")

    st.write(f"""
    Total Receivables: ${total_ar:,.0f}

    Overdue Receivables: ${overdue:,.0f}

    Overdue Percentage: {overdue_percent:.1f}%

    High Risk Debt (90+ days): ${high_risk:,.0f}

    Bad Debt Risk (120+ days): ${bad_debt:,.0f}
    """)
