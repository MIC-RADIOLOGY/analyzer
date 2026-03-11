import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("Accounts Receivable Aging Analyzer")
st.write("Upload an aging report to analyze receivables automatically.")

# -------------------------------
# Automatic Column Detection
# -------------------------------
def detect_columns(df):
    mapping = {}
    for c in df.columns:
        c_lower = c.lower()
        if "provider" in c_lower or "debtor" in c_lower:
            mapping["provider"] = c
        elif "balance" in c_lower:
            mapping["balance"] = c
        elif "current" in c_lower:
            mapping["current"] = c
        elif "30" in c_lower:
            mapping["30"] = c
        elif "60" in c_lower:
            mapping["60"] = c
        elif "90" in c_lower:
            mapping["90"] = c
        elif "120" in c_lower:
            mapping["120"] = c
        elif "150" in c_lower:
            mapping["150"] = c
        elif "180" in c_lower:
            mapping["180"] = c
        elif "unalloc" in c_lower:
            mapping["unallocated"] = c
    return mapping

# -------------------------------
# Upload File
# -------------------------------
uploaded_file = st.file_uploader("Upload Aging Report", type=["xlsx", "csv"])

if uploaded_file:
    # Load file
    if uploaded_file.name.endswith("xlsx"):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)

    st.subheader("Uploaded Data")
    st.dataframe(df)

    # Detect columns automatically
    mapping = detect_columns(df)

    # -------------------------------
    # Calculate Totals and KPIs
    # -------------------------------
    balance = mapping["balance"]
    current = mapping["current"]
    d30 = mapping["30"]
    d60 = mapping["60"]
    d90 = mapping["90"]
    d120 = mapping["120"]
    d150 = mapping["150"]
    d180 = mapping["180"]
    provider = mapping["provider"]
    unallocated = mapping["unallocated"]

    total_ar = df[balance].sum()
    current_total = df[current].sum()
    d30_total = df[d30].sum()
    d60_total = df[d60].sum()
    d90_total = df[d90].sum()
    d120_total = df[d120].sum()
    d150_total = df[d150].sum()
    d180_total = df[d180].sum()
    unallocated_total = df[unallocated].sum()

    overdue = total_ar - current_total
    adjusted_receivables = total_ar - abs(unallocated_total)
    overdue_percent = overdue / total_ar * 100
    high_risk = d90_total + d120_total + d150_total + d180_total
    bad_debt = d120_total + d150_total + d180_total

    # -------------------------------
    # KPI Dashboard
    # -------------------------------
    st.subheader("Key Financial Metrics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Receivables", f"${total_ar:,.0f}")
    col2.metric("Adjusted Receivables", f"${adjusted_receivables:,.0f}")
    col3.metric("Overdue", f"${overdue:,.0f}")
    col4.metric("Overdue %", f"{overdue_percent:.1f}%")

    # -------------------------------
    # Aging Distribution Chart
    # -------------------------------
    aging_data = pd.DataFrame({
        "Bucket":["180+","150","120","90","60","30","Current"],
        "Amount":[d180_total,d150_total,d120_total,d90_total,d60_total,d30_total,current_total]
    })
    fig = px.bar(aging_data, x="Bucket", y="Amount", title="Accounts Receivable Aging Distribution")
    st.plotly_chart(fig, use_container_width=True)

    # -------------------------------
    # Top Debtors Chart
    # -------------------------------
    st.subheader("Top Debtors")
    top_debtors = df.sort_values(balance, ascending=False).head(10)
    fig2 = px.bar(top_debtors, x=provider, y=balance, title="Top 10 Debtors")
    st.plotly_chart(fig2, use_container_width=True)

    # -------------------------------
    # Credit Balances
    # -------------------------------
    st.subheader("Providers With Credit Balances")
    credit_balances = df[df[unallocated] < 0]
    st.dataframe(credit_balances[[provider, unallocated]])

    # -------------------------------
    # Management Insights
    # -------------------------------
    st.subheader("Management Insights")
    top3_total = top_debtors.head(3)[balance].sum()
    concentration = top3_total / total_ar * 100

    st.write(f"""
**Total Receivables:** ${total_ar:,.0f}  
**Adjusted Receivables:** ${adjusted_receivables:,.0f}  
**Overdue Receivables:** ${overdue:,.0f} ({overdue_percent:.1f}%)  
**High Risk Debt (90+ days):** ${high_risk:,.0f}  
**Bad Debt Risk (120+ days):** ${bad_debt:,.0f}  
**Debtor Concentration (Top 3):** {concentration:.1f}%

**Recommendation:** Focus collection efforts on the largest debtors and review balances older than 120 days.
""")
