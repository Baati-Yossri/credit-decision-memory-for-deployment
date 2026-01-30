import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer

# ===============================
# LOAD DATA
# ===============================
df = pd.read_csv("data/loan_applications_synthetic_time.csv")

# ===============================
# DEFINE VECTOR FEATURES
# ===============================
numerical_features = [
    "monthly_income",
    "existing_emis_monthly",
    "debt_to_income_ratio",
    "loan_amount_requested",
    "loan_tenure_months",
    "interest_rate_offered",
    "cibil_score",
    "applicant_age",
    "number_of_dependents"
]

categorical_features = [
    "employment_status",
    "property_ownership_status",
    "loan_type",
    "purpose_of_loan"
]

# ===============================
# PREPROCESSOR
# ===============================
preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), numerical_features),
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features)
    ]
)

# ===============================
# BUILD VECTORS
# ===============================

vectors = preprocessor.fit_transform(df)

# Convert to dense array (required for Qdrant)
# vectors = vectors.toarray()

print("✅ Vectorization complete")
print("Number of loan cases:", vectors.shape[0])
print("Vector dimension:", vectors.shape[1])


import joblib

joblib.dump(preprocessor, "vector_preprocessor.joblib")
np.save("loan_vectors.npy", vectors)

print("💾 Preprocessor and vectors saved")
