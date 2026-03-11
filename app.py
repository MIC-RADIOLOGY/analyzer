import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("Accounts Receivable Aging Analyzer")

# -------------------------------
# Detect correct header row
# -------------------------------
def load_excel_with_correct_header(file):

    preview = pd.read_excel(file, header=None)

    header_row = 0

    for i in range(len(preview)):
        row_text = " ".join(str(x).lower() for x in preview.iloc[i])

        if "provider" in row_text or "debtor" in row_text:
            header_row = i
            break

    df = pd.read_excel(file, header=header_row)

    df.columns = df.columns.str.strip()

    return df


# -------------------------------
# Detect aging columns
# -------------------------------
def detect_columns(df):

    mapping = {}

    for col in df.columns:

        c = col.lower().strip()

        if "provider" in c or "debtor" in c:
            mapping["provider"] = col

        elif "balance" in c or "outstanding" in c or "total" in c:
            mapping["balance"] = col

        elif "current" in c:
            mapping["current"] = col

        elif "30" in c:
            mapping["30"] = col

        elif "60" in c:
            mapping["60"] = col

        elif "90" in c:
            mapping["90"] = col

        elif "120" in c:
            mapping["120"] = col

        elif "150" in c:
            mapping["150"] = col

        elif "180" in c or "over" in c:
            mapping["180"] = col

        elif "unalloc" in c or "credit" in c:
            mapping["unallocated"] = col

    return mapping


# -------------------------------
# Upload file
# -------------------------------
uploaded_file = st.file_uploader(
    "Upload Aging Report",
    type=["xlsx", "csv"]
)

if uploaded_file:

    if uploaded_file.name.endswith("xlsx"):
        df = load_excel_with_correct_header(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)

    st.subheader("Uploaded Data")
    st.dataframe(df)

    st.subheader("Detected Columns")

    mapping = detect_columns(df)

    st.write(mapping)

    required = [
        "provider",
        "balance",
        "current",
        "30",
        "60",
        "90",
        "120",
        "150",
        "180",
        "unallocated"
    ]

    missing = [r for r in required if r not in mapping]

    if missing:

        st.error(f"Missing columns: {missing}")

    else:

        # -------------------------------
        # Calculate totals
        # -------------------------------
        total_ar = df[mapping["balance"]].sum()

        current_total = df[mapping["current"]].sum()

        d30 = df[mapping["30"]].sum()
        d60 = df[mapping["60"]].sum()
        d90 = df[mapping["90"]].sum()
        d120 = df[mapping["120"]].sum()
        d150 = df[mapping["150"]].sum()
        d180 = df[mapping["180"]].sum()

        unallocated_total = df[mapping["unallocated"]].sum()

        overdue = total_ar - current_total

        adjusted_receivables = total_ar - abs(unallocated_total)

        overdue_percent = overdue / total_ar * 100

        high_risk = d90 + d120 + d150 + d180

        bad_debt = d120 + d150 + d180

        # -------------------------------
        # KPI Dashboard
        # -------------------------------
        st.subheader("Key Financial Metrics")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Total Receivables", f"${total_ar:,.0f}")
        c2.metric("Adjusted Receivables", f"${adjusted_receivables:,.0f}")
        c3.metric("Overdue", f"${overdue:,.0f}")
        c4.metric("Overdue %", f"{overdue_percent:.1f}%")

        # -------------------------------
        # Aging chart
        # -------------------------------
        aging = pd.DataFrame({
            "Bucket": ["180+", "150", "120", "90", "60", "30", "Current"],
            "Amount": [d180, d150, d120, d90, d60, d30, current_total]
        })

        fig = px.bar(
            aging,
            x="Bucket",
            y="Amount",
            title="Aging Distribution"
        )

        st.plotly_chart(fig, use_container_width=True)

        # -------------------------------
        # Top Debtors
        # -------------------------------
        st.subheader("Top Debtors")

        top = df.sort_values(
            mapping["balance"],
            ascending=False
        ).head(10)

        fig2 = px.bar(
            top,
            x=mapping["provider"],
            y=mapping["balance"],
            title="Top 10 Debtors"
        )

        st.plotly_chart(fig2, use_container_width=True)

        # -------------------------------
        # Credit balances
        # -------------------------------
        st.subheader("Providers With Credit Balances")

        credit = df[df[mapping["unallocated"]] < 0]

        st.dataframe(
            credit[
                [
                    mapping["provider"],
                    mapping["unallocated"]
                ]
            ]
        )

        # -------------------------------
        # Management insights
        # -------------------------------
        st.subheader("Management Insights")

        top3 = top.head(3)[mapping["balance"]].sum()

        concentration = top3 / total_ar * 100

        st.write(f"""
Total Receivables: ${total_ar:,.0f}

Adjusted Receivables: ${adjusted_receivables:,.0f}

Overdue Receivables: ${overdue:,.0f}

Overdue Percentage: {overdue_percent:.1f}%

High Risk Debt (90+ days): ${high_risk:,.0f}

Bad Debt Risk (120+ days): ${bad_debt:,.0f}

Top 3 Debtors Concentration: {concentration:.1f}%
""")
