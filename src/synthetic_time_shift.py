import pandas as pd
import numpy as np
from datetime import datetime

# ===============================
# CONFIG
# ===============================
SHIFT_MONTHS = 36   # 3 years back in time
TODAY = pd.Timestamp(datetime.now().date())

# ===============================
# LOAD DATA
# ===============================
df = pd.read_csv("data/loan_applications_final.csv")

# ===============================
# PARSE DATES
# ===============================
df["application_date"] = pd.to_datetime(df["application_date"], errors="coerce")

# ===============================
# SYNTHETIC TIME SHIFT
# ===============================
df["shifted_application_date"] = df["application_date"] - pd.DateOffset(months=SHIFT_MONTHS)

# ===============================
# COMPUTE LOAN AGE
# ===============================
df["loan_age_months"] = (
    (TODAY - df["shifted_application_date"]).dt.days / 30.44
).round(1)

# ===============================
# REDEFINE OUTCOME (TIME-AWARE)
# ===============================
df["loan_outcome"] = "In_Progress"

# Defaulted
df.loc[
    (df["fraud_flag"] == 1) |
    (df["time_to_default_months"].notna() & (df["time_to_default_months"] <= 6)),
    "loan_outcome"
] = "Defaulted"

# Repaid
df.loc[
    (df["loan_age_months"] >= df["loan_tenure_months"]) &
    (df["fraud_flag"] == 0) &
    (~((df["time_to_default_months"].notna()) & (df["time_to_default_months"] <= 6))),
    "loan_outcome"
] = "Repaid"

# ===============================
# SAVE NEW DATASET
# ===============================
df.to_csv("data/loan_applications_synthetic_time.csv", index=False)

# ===============================
# DISTRIBUTION CHECK
# ===============================
print("\n📊 New outcome distribution (synthetic time-aware):")
print(df["loan_outcome"].value_counts(normalize=True) * 100)

print("\n✅ Synthetic time shifting complete.")
