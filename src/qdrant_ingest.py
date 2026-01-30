import pandas as pd
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
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
BATCH_SIZE = 500   # safe for cloud

# ===============================
# LOAD DATA
# ===============================
df = pd.read_csv("data/loan_applications_synthetic_time.csv")
vectors = np.load("data/loan_vectors.npy")

client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    # check_compatibility=False,
    timeout=60.0   # increase timeout
)

# ===============================
# BATCHED INGESTION
# ===============================
total_points = len(df)

for start in range(0, total_points, BATCH_SIZE):
    end = min(start + BATCH_SIZE, total_points)

    points = []

    for idx in range(start, end):
        row = df.iloc[idx]

        payload = {
            "application_id": row["application_id"],
            "loan_status": row["loan_status"],
            "loan_outcome": row["loan_outcome"],
            "fraud_flag": int(row["fraud_flag"]),
            "fraud_type": row["fraud_type"],
            "loan_type": row["loan_type"],
            "purpose_of_loan": row["purpose_of_loan"],
            "time_to_default_months": (
                None if pd.isna(row["time_to_default_months"])
                else int(row["time_to_default_months"])
            )
        }

        points.append(
            PointStruct(
                id=idx,
                vector=vectors[idx],
                payload=payload
            )
        )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )

    print(f"✅ Uploaded points {start} → {end}")

print("🎉 All loan cases ingested successfully")
