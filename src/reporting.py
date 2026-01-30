from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle
)
from reportlab.lib import colors
from datetime import datetime


class DecisionReportGenerator:
    """
    Generates an audit-ready, similarity-based credit decision report.
    """

    def generate(self, output_path, application_data, result_summary, chart_path=None):
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        story = []

        # ===============================
        # CUSTOM STYLES
        # ===============================
        title_style = ParagraphStyle(
            "Title",
            parent=styles["Title"],
            alignment=TA_CENTER,
            fontSize=18,
            spaceAfter=20
        )

        header_style = ParagraphStyle(
            "Header",
            parent=styles["Heading2"],
            spaceBefore=16,
            spaceAfter=10
        )

        body_style = ParagraphStyle(
            "Body",
            parent=styles["BodyText"],
            spaceAfter=10
        )

        subtle_style = ParagraphStyle(
            "Subtle",
            parent=styles["BodyText"],
            textColor=colors.grey,
            fontSize=9
        )

        # ===============================
        # TITLE PAGE HEADER
        # ===============================
        story.append(Paragraph("Credit Decision Memory Report", title_style))
        story.append(Paragraph(
            f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            subtle_style
        ))
        story.append(Spacer(1, 20))

        # ===============================
        # EXECUTIVE SUMMARY
        # ===============================
        story.append(Paragraph("Executive Summary", header_style))
        story.append(Paragraph(
            "This report provides similarity-based decision support for a newly submitted loan "
            "application. The system does not automate approval or rejection. Instead, it retrieves "
            "historical loan cases with comparable characteristics and summarizes their observed "
            "outcomes to assist human decision-makers.",
            body_style
        ))

        # ===============================
        # APPLICATION SNAPSHOT
        # ===============================
        story.append(Paragraph("Application Snapshot", header_style))

        app_table_data = [
            ["Attribute", "Value"],
            ["Monthly Income", f"${application_data['monthly_income']:,}"],
            ["Existing Monthly EMIs", f"${application_data['existing_emis_monthly']:,}"],
            ["Debt-to-Income Ratio", f"{application_data['debt_to_income_ratio']:.2f}"],
            ["Loan Amount Requested", f"${application_data['loan_amount_requested']:,}"],
            ["Loan Tenure (Months)", application_data["loan_tenure_months"]],
            ["Credit Score", application_data["cibil_score"]],
            ["Applicant Age", application_data["applicant_age"]],
            ["Number of Dependents", application_data["number_of_dependents"]],
            ["Employment Status", application_data["employment_status"]],
            ["Property Ownership", application_data["property_ownership_status"]],
            ["Loan Type", application_data["loan_type"]],
            ["Purpose of Loan", application_data["purpose_of_loan"]],
        ]

        app_table = Table(app_table_data, colWidths=[200, 300])
        app_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
        ]))

        story.append(app_table)

        # ===============================
        # SIMILARITY METHODOLOGY
        # ===============================
        story.append(Spacer(1, 16))
        story.append(Paragraph("Similarity Methodology", header_style))
        story.append(Paragraph(
            "Historical loan cases were retrieved based on vector similarity across multiple "
            "financial and contextual attributes, including income level, loan amount, credit score, "
            "loan tenure, employment status, property ownership, and loan purpose.",
            body_style
        ))
        story.append(Paragraph(
            "This approach ensures that comparisons are made against economically and behaviorally "
            "comparable cases rather than relying on abstract predictive scores.",
            body_style
        ))

        # ===============================
        # HISTORICAL OUTCOME ANALYSIS
        # ===============================
        story.append(Paragraph("Historical Outcome Analysis", header_style))

        total = result_summary["total_cases"]
        repaid = result_summary["repaid_pct"]
        defaulted = result_summary["defaulted_pct"]
        in_progress = result_summary["in_progress_pct"]
        fraud = result_summary["fraud_cases"]

        story.append(Paragraph(
            f"The system identified {total} historical loan cases with similar characteristics. "
            f"Among these cases, {repaid:.1f}% were successfully repaid, "
            f"{defaulted:.1f}% resulted in default, and "
            f"{in_progress:.1f}% are still in progress. "
            f"{fraud} cases were associated with confirmed fraud signals.",
            body_style
        ))

        # ===============================
        # EMBED CHART
        # ===============================
        if chart_path:
            story.append(Spacer(1, 12))
            story.append(Image(chart_path, width=300, height=300))

        # ===============================
        # RISK & POSITIVE SIGNALS
        # ===============================
        story.append(Paragraph("Observed Risk and Positive Signals", header_style))

        risk_signals = []
        positive_signals = []

        if defaulted > 50:
            risk_signals.append("High default rate among similar historical cases.")
        if fraud > 0:
            risk_signals.append("Presence of fraud cases in the similarity set.")
        if application_data["debt_to_income_ratio"] > 0.4:
            risk_signals.append("Elevated debt-to-income ratio compared to peer cases.")

        if application_data["cibil_score"] >= 750:
            positive_signals.append("Strong credit score relative to similar applicants.")
        if application_data["property_ownership_status"] == "Owned":
            positive_signals.append("Property ownership associated with improved repayment resilience.")
        if repaid > defaulted:
            positive_signals.append("Majority of similar cases resulted in successful repayment.")

        story.append(Paragraph("<b>Risk Signals</b>", body_style))
        for r in risk_signals or ["No dominant risk signals identified."]:
            story.append(Paragraph(f"- {r}", body_style))

        story.append(Spacer(1, 8))
        story.append(Paragraph("<b>Positive Signals</b>", body_style))
        for p in positive_signals or ["No strong positive signals identified."]:
            story.append(Paragraph(f"- {p}", body_style))

        # ===============================
        # DECISION SUPPORT STATEMENT
        # ===============================
        story.append(Paragraph("Decision Support Statement", header_style))
        story.append(Paragraph(
            "This similarity-based assessment suggests how comparable loans have historically "
            "performed under similar conditions. It is intended to support, not replace, human "
            "judgment. Final credit decisions should incorporate institutional policies, regulatory "
            "requirements, and current economic context.",
            body_style
        ))

        # ===============================
        # DISCLAIMER
        # ===============================
        story.append(Spacer(1, 16))
        story.append(Paragraph(
            "Disclaimer: This report is generated using historical similarity analysis and does not "
            "constitute a predictive credit score or automated decision.",
            subtle_style
        ))

        # ===============================
        # BUILD DOCUMENT
        # ===============================
        doc.build(story)
