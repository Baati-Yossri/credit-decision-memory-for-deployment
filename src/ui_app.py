import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from similarity_engine import find_similar_loans
from reporting import DecisionReportGenerator

# ======================================================
# Page config
# ======================================================
st.set_page_config(
    page_title="Credit Decision Memory",
    layout="wide"
)

st.title("🏦 Credit Decision Memory")
st.caption("Similarity-Driven Risk & Anomaly Detection")

# ======================================================
# Default loan case (GOOD CASE)
# ======================================================
default_loan = {
    "monthly_income": 5000,
    "existing_emi": 800,
    "debt_to_income": 0.16,
    "loan_amount": 15000,
    "loan_tenure_months": 36,
    "credit_score": 780,
    "age": 35,
    "dependents": 2,
    "employment_status": "Salaried",
    "property_ownership": "Owned",
    "loan_type": "Personal Loan",
    "loan_purpose": "Home Improvement"
}

# ======================================================
# UI – Input form
# ======================================================
with st.form("loan_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        monthly_income = st.number_input(
            "Monthly Income ($)",
            value=default_loan["monthly_income"]
        )
        existing_emi = st.number_input(
            "Existing Monthly EMIs ($)",
            value=default_loan["existing_emi"]
        )
        debt_to_income = st.number_input(
            "Debt-to-Income Ratio",
            value=default_loan["debt_to_income"]
        )
        credit_score = st.number_input(
            "Credit Score",
            value=default_loan["credit_score"]
        )

    with col2:
        loan_amount = st.number_input(
            "Loan Amount Requested ($)",
            value=default_loan["loan_amount"]
        )
        loan_tenure = st.number_input(
            "Loan Tenure (Months)",
            value=default_loan["loan_tenure_months"]
        )
        age = st.number_input(
            "Applicant Age",
            value=default_loan["age"]
        )
        dependents = st.number_input(
            "Number of Dependents",
            value=default_loan["dependents"]
        )

    with col3:
        employment_status = st.selectbox(
            "Employment Status",
            ["Salaried", "Self-Employed"],
            index=0
        )
        property_ownership = st.selectbox(
            "Property Ownership",
            ["Owned", "Mortgaged", "Rented"],
            index=0
        )
        loan_type = st.selectbox(
            "Loan Type",
            ["Personal Loan", "Auto Loan", "Home Loan"],
            index=0
        )
        loan_purpose = st.selectbox(
            "Purpose of Loan",
            ["Home Improvement", "Business", "Education", "Medical"],
            index=0
        )

    submitted = st.form_submit_button("🔍 Analyze Loan Case")

# ======================================================
# Run analysis
# ======================================================
if submitted:
    application_data = {
        "monthly_income": monthly_income,
        "existing_emi": existing_emi,
        "debt_to_income": debt_to_income,
        "loan_amount": loan_amount,
        "loan_tenure_months": loan_tenure,
        "credit_score": credit_score,
        "age": age,
        "dependents": dependents,
        "employment_status": employment_status,
        "property_ownership": property_ownership,
        "loan_type": loan_type,
        "loan_purpose": loan_purpose
    }

    with st.spinner("Retrieving similar historical cases..."):
        result = find_similar_loans(application_data)

    st.success("Similarity analysis completed")

    # ==================================================
    # Metrics
    # ==================================================
    m1, m2, m3, m4 = st.columns(4)

    m1.metric("Total Similar Cases", result["total_cases"])
    m2.metric("Repaid (%)", f"{result['repaid_pct']:.1f}")
    m3.metric("Defaulted (%)", f"{result['defaulted_pct']:.1f}")
    m4.metric("Fraud Cases", result["fraud_cases"])

    # ==================================================
    # Plotly chart (UI only)
    # ==================================================
    chart_df = pd.DataFrame({
        "Outcome": ["Repaid", "Defaulted", "In Progress"],
        "Percentage": [
            result["repaid_pct"],
            result["defaulted_pct"],
            result["in_progress_pct"]
        ]
    })

    fig = px.bar(
        chart_df,
        x="Outcome",
        y="Percentage",
        title="Outcome Distribution (Similarity-Based)",
        text_auto=True
    )

    st.plotly_chart(fig, width="stretch")

    # ==================================================
    # Matplotlib chart (PDF-SAFE)
    # ==================================================
    fig_mpl, ax = plt.subplots(figsize=(6, 4))

    ax.bar(
        chart_df["Outcome"],
        chart_df["Percentage"]
    )

    ax.set_ylabel("Percentage (%)")
    ax.set_title("Outcome Distribution")

    plt.tight_layout()

    chart_path = "outcome_distribution.png"
    plt.savefig(chart_path)
    plt.close()

    st.session_state.chart_path = chart_path

    # ==================================================
    # Table of similar cases
    # ==================================================
    if result["cases"]:
        st.subheader("📄 Similar Historical Cases")
        st.dataframe(pd.DataFrame(result["cases"]))

    # ==================================================
    # PDF Report
    # ==================================================
    st.subheader("📄 Decision Report")

    if st.button("Generate PDF Report"):
        generator = DecisionReportGenerator()
        pdf_path = generator.generate(
            application_data=application_data,
            analysis_result=result,
            chart_path=chart_path
        )

        with open(pdf_path, "rb") as f:
            st.download_button(
                "⬇️ Download Decision Report",
                f,
                file_name="credit_decision_report.pdf",
                mime="application/pdf"
            )
