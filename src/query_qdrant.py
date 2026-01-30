import pandas as pd
import joblib
from qdrant_client import QdrantClient
import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env from project root
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

QDRANT_URL = os.getenv("url")
QDRANT_API_KEY = os.getenv("Api")

if not QDRANT_URL or not QDRANT_API_KEY:
    raise ValueError("Missing QDRANT_URL or QDRANT_API_KEY in .env")


# ===============================
# CONFIG
# ===============================
COLLECTION_NAME = "credit_decision_memory"
TOP_K = 10


# ===============================
# CONNECT TO QDRANT CLOUD
# ===============================
client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    timeout=60.0
)

# ===============================
# LOAD PREPROCESSOR
# ===============================
preprocessor = joblib.load("src/vector_preprocessor.joblib")

# ===============================
# NEW LOAN APPLICATION (EXAMPLE)
# ===============================
# new_application = {
#     "monthly_income": 5000,
#     "existing_emis_monthly": 1200,
#     "debt_to_income_ratio": 0.50,
#     "loan_amount_requested": 20000,
#     "loan_tenure_months": 36,
#     "interest_rate_offered": 12.5,
#     "cibil_score": 680,
#     "applicant_age": 34,
#     "number_of_dependents": 2,
#     "employment_status": "Salaried",
#     "property_ownership_status": "Rented",
#     "loan_type": "Personal Loan",
#     "purpose_of_loan": "Education"
# }
new_application = {
    "monthly_income": 10000,                 # higher stable income
    "existing_emis_monthly": 900,           # low existing obligations
    "debt_to_income_ratio": 0.10,            # healthy DTI
    "loan_amount_requested": 10000,          # reasonable loan size
    "loan_tenure_months": 24,                # shorter tenure
    "interest_rate_offered": 9.5,            # lower interest rate
    "cibil_score": 760,                      # strong credit score
    "applicant_age": 32,                     # prime working age
    "number_of_dependents": 1,               # manageable dependents
    "employment_status": "Salaried",         # stable job
    "property_ownership_status": "Owned",    # asset ownership
    "loan_type": "Personal Loan",
    "purpose_of_loan": "Home Improvement"    # practical, low-risk purpose
}


# ===============================
# VECTORIZE APPLICATION
# ===============================
X_new_df = pd.DataFrame([new_application])
X_new = preprocessor.transform(X_new_df)

# ColumnTransformer may return sparse
if hasattr(X_new, "toarray"):
    X_new = X_new.toarray()

query_vector = X_new[0]

# ===============================
# VECTOR SEARCH (CORRECT FOR 1.7.3)
# ===============================
results = client.search(
    collection_name=COLLECTION_NAME,
    query_vector=query_vector,
    limit=TOP_K
)

# ===============================
# ANALYZE RESULTS
# ===============================
outcomes = {"Repaid": 0, "Defaulted": 0, "Not_Applicable": 0}
fraud_count = 0

print("\n🔎 Similar historical loan cases:\n")

for i, hit in enumerate(results, start=1):
    payload = hit.payload

    outcome = payload.get("loan_outcome", "Unknown")
    fraud_flag = payload.get("fraud_flag", 0)

    if outcome in outcomes:
        outcomes[outcome] += 1
    if fraud_flag == 1:
        fraud_count += 1

    print(
        f"{i}. Outcome: {outcome} | "
        f"Fraud: {fraud_flag} | "
        f"Loan Type: {payload.get('loan_type')} | "
        f"Purpose: {payload.get('purpose_of_loan')}"
    )

# ===============================
# BANKER-FRIENDLY EXPLANATION
# ===============================
print("\n📊 Decision Support Summary")
print(f"Top {TOP_K} similar cases:")
print(f"  • Repaid: {outcomes['Repaid']}")
print(f"  • Defaulted: {outcomes['Defaulted']}")
print(f"  • Fraud cases: {fraud_count}")

if fraud_count > 0:
    insight = "⚠️ Similar fraud patterns detected. Manual review recommended."
elif outcomes["Defaulted"] > outcomes["Repaid"]:
    insight = "⚠️ Majority of similar cases defaulted. High observed risk."
else:
    insight = "✅ Majority of similar cases were repaid. Lower observed risk."

print("\n🧠 Insight for banker:")
print(insight)



