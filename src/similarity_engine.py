import os
import joblib
import numpy as np
import pandas as pd
import streamlit as st
from pathlib import Path
from qdrant_client import QdrantClient

# ======================================================
# Environment variables (Streamlit Cloud compatible)
# ======================================================
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

if not QDRANT_URL or not QDRANT_API_KEY:
    raise RuntimeError(
        "Missing QDRANT_URL or QDRANT_API_KEY. "
        "Set them in Streamlit Cloud → App Settings → Secrets."
    )

# ======================================================
# Constants
# ======================================================
COLLECTION_NAME = "credit_decision_memory"
TOP_K = 10

# ======================================================
# Load vector preprocessor (joblib)
# ======================================================
BASE_DIR = Path(__file__).resolve().parent
PREPROCESSOR_PATH = BASE_DIR / "vector_preprocessor.joblib"

if not PREPROCESSOR_PATH.exists():
    raise FileNotFoundError(
        f"Preprocessor file not found: {PREPROCESSOR_PATH}"
    )

preprocessor = joblib.load(PREPROCESSOR_PATH)

# ======================================================
# Qdrant client (cached for Streamlit)
# ======================================================
@st.cache_resource
def get_qdrant_client():
    return QdrantClient(
        url=QDRANT_URL,          # MUST be https://xxx.qdrant.tech
        api_key=QDRANT_API_KEY,
        timeout=60
    )

client = get_qdrant_client()

# ======================================================
# Similarity search function
# ======================================================
def find_similar_loans(loan_dict, k=TOP_K):
    """
    Given a loan application dict, return similarity-based
    decision insights from Qdrant.
    """

    # Convert input to DataFrame
    df = pd.DataFrame([loan_dict])

    # Vectorize
    X = preprocessor.transform(df)

    if hasattr(X, "toarray"):
        vector = X.toarray()[0].tolist()
    else:
        vector = X[0].tolist()

    # Query Qdrant
    try:
        results = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=vector,
            limit=k
        )
    except Exception as e:
        raise RuntimeError(f"Qdrant search failed: {e}")

    payloads = [r.payload for r in results]
    scores = [r.score for r in results]

    if not payloads:
        return {
            "total_cases": 0,
            "repaid_pct": 0,
            "defaulted_pct": 0,
            "in_progress_pct": 0,
            "fraud_cases": 0,
            "avg_similarity": 0,
            "cases": []
        }

    outcomes = [p.get("loan_outcome") for p in payloads]
    frauds = [p.get("fraud_flag", 0) for p in payloads]
    total = len(outcomes)

    return {
        "total_cases": total,
        "repaid_pct": outcomes.count("Repaid") / total * 100,
        "defaulted_pct": outcomes.count("Defaulted") / total * 100,
        "in_progress_pct": outcomes.count("In Progress") / total * 100,
        "fraud_cases": int(sum(frauds)),
        "avg_similarity": float(np.mean(scores)),
        "cases": payloads
    }
