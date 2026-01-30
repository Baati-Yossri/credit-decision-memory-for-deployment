import streamlit as st
import pandas as pd
import plotly.express as px
from similarity_engine import find_similar_loans
from reporting import DecisionReportGenerator

# ===============================
# SESSION STATE
# ===============================
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

if "application_data" not in st.session_state:
    st.session_state.application_data = None

if "chart_path" not in st.session_state:
    st.session_state.chart_path = None

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(
    page_title="Credit Decision Memory",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===============================
# LOAD CUSTOM CSS
# ===============================
def load_css():
    try:
        with open("src/styles.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

load_css()

# ===============================
# HEADER
# ===============================
st.title("🏦 Credit Decision Memory System")
st.markdown("Similarity-based decision support for loan underwriting.")

# ===============================
# SIDEBAR — INPUT FORM
# ===============================
with st.sidebar:
    st.header("Loan Application Details")

    monthly_income = st.number_input(
        "Monthly Income ($)", min_value=1000, max_value=50000, value=10000, step=500
    )

    loan_amount = st.number_input(
        "Loan Amount Requested ($)", min_value=1000, max_value=100000, value=10000, step=500
    )

    loan_tenure = st.slider("Loan Tenure (Months)", 6, 60, 24)

    cibil_score = st.slider("Credit Score", 300, 900, 760)

    existing_emis = st.number_input(
        "Existing Monthly EMIs ($)", min_value=0, max_value=20000, value=900, step=100
    )

    loan_type = st.selectbox(
        "Loan Type", ["Personal Loan", "Auto Loan", "Home Loan", "Education Loan"]
    )

    employment_status = st.selectbox(
        "Employment Status", ["Salaried", "Self-Employed", "Unemployed", "Student"]
    )

    property_ownership = st.selectbox(
        "Property Ownership", ["Owned", "Rented", "Mortgaged"]
    )

    purpose_of_loan = st.selectbox(
        "Purpose",
        ["Home Improvement", "Education", "Medical", "Wedding", "Business", "Other"]
    )

    applicant_age = st.slider("Applicant Age", 18, 70, 32)
    dependents = st.number_input("Number of Dependents", 0, 10, 1)

    analyze_btn = st.button("Analyze Loan Case", type="primary")

# ===============================
# MAIN CONTENT
# ===============================
if analyze_btn or st.session_state.analysis_result is not None:

    if analyze_btn:
        debt_to_income = existing_emis / monthly_income if monthly_income > 0 else 0

        application_data = {
            "monthly_income": monthly_income,
            "existing_emis_monthly": existing_emis,
            "debt_to_income_ratio": debt_to_income,
            "loan_amount_requested": loan_amount,
            "loan_tenure_months": loan_tenure,
            "interest_rate_offered": 9.5,
            "cibil_score": cibil_score,
            "applicant_age": applicant_age,
            "number_of_dependents": dependents,
            "employment_status": employment_status,
            "property_ownership_status": property_ownership,
            "loan_type": loan_type,
            "purpose_of_loan": purpose_of_loan
        }

        with st.spinner("Retrieving similar historical cases..."):
            st.session_state.analysis_result = find_similar_loans(application_data, k=10)
            st.session_state.application_data = application_data

    result = st.session_state.analysis_result
    application_data = st.session_state.application_data

    total_cases = result["total_cases"]
    repaid_pct = result["repaid_pct"]
    defaulted_pct = result["defaulted_pct"]
    fraud_cases = result["fraud_cases"]

    # ===============================
    # RISK SEGMENT
    # ===============================
    if defaulted_pct > 60:
        risk_segment = "High Risk (Similarity-Based)"
        alert_class = "alert-danger"
        emoji = "🚨"
    elif defaulted_pct > 30:
        risk_segment = "Moderate Risk (Similarity-Based)"
        alert_class = "alert-warning"
        emoji = "⚠️"
    else:
        risk_segment = "Low Risk (Similarity-Based)"
        alert_class = "alert-success"
        emoji = "✅"

    st.divider()
    st.markdown(
        f'<div class="{alert_class}">{emoji} <strong>Assessment: {risk_segment}</strong></div>',
        unsafe_allow_html=True
    )

    # ===============================
    # METRICS
    # ===============================
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Similar Cases", total_cases)
    with col2:
        st.metric("Repayment Rate (Similar)", f"{repaid_pct:.1f}%")
    with col3:
        st.metric("Fraud Signals Detected", fraud_cases, delta_color="inverse")

    # ===============================
    # CHART + TABLE
    # ===============================
    col_chart, col_table = st.columns(2)

    # ---- FIXED PIE CHART LOGIC ----
    with col_chart:
        st.subheader("Outcome Distribution")

        outcome_counts = {"Repaid": 0, "Defaulted": 0, "In Progress": 0}

        for case in result["cases"]:
            outcome = case.get("loan_outcome")
            if outcome == "Repaid":
                outcome_counts["Repaid"] += 1
            elif outcome == "Defaulted":
                outcome_counts["Defaulted"] += 1
            else:
                outcome_counts["In Progress"] += 1

        outcome_df = pd.DataFrame({
            "Outcome": list(outcome_counts.keys()),
            "Count": list(outcome_counts.values())
        })

        fig = px.pie(
            outcome_df,
            values="Count",
            names="Outcome",
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.RdBu
        )

        fig.update_traces(textinfo="percent+label")

        st.plotly_chart(fig, use_container_width=True)

        chart_path = "outcome_distribution.png"
        fig.write_image(chart_path)
        st.session_state.chart_path = chart_path

    with col_table:
        st.subheader("Top Similar Cases")
        table_data = []
        for case in result["cases"]:
            table_data.append({
                "Outcome": case.get("loan_outcome"),
                "Fraud": "Yes" if case.get("fraud_flag") == 1 else "No",
                "Loan Type": case.get("loan_type"),
                "Purpose": case.get("purpose_of_loan")
            })
        st.dataframe(table_data, use_container_width=True)

    # ===============================
    # EXPLANATION
    # ===============================
    st.subheader("🤖 System Explanation")
    st.info(
        f"The system retrieved {total_cases} historical loan cases with similar "
        f"income levels, loan amounts, credit scores, and loan purposes. "
        f"Among these cases, {repaid_pct:.1f}% were successfully repaid, while "
        f"{defaulted_pct:.1f}% resulted in default. "
        f"This assessment is based on similarity to past observed outcomes, "
        f"not on predictive modeling."
    )

    # ===============================
    # PDF REPORT
    # ===============================
    st.divider()
    if st.button("📄 Generate PDF Decision Report"):
        report = DecisionReportGenerator()
        report_path = "Credit_Decision_Report.pdf"

        report.generate(
            output_path=report_path,
            application_data=application_data,
            result_summary=result,
            chart_path=st.session_state.chart_path
        )

        with open(report_path, "rb") as f:
            st.download_button(
                "⬇️ Download PDF Report",
                f,
                file_name="Credit_Decision_Report.pdf",
                mime="application/pdf"
            )

else:
    st.info("👈 Enter loan details in the sidebar and click **Analyze Loan Case** to begin.")

st.markdown("---")
st.caption("Credit Decision Memory System | Team Weavers | Internal Prototype v1.0")
