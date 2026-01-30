# 🏦 Credit Decision Memory

**Similarity-Driven Risk & Anomaly Detection using Qdrant**

**Team:** Weavers  
**Hackathon Use Case:** Credit Decision Memory (Use Case 3)

---

## 1. Project Overview

**Credit Decision Memory** is a similarity-based decision support system designed to assist loan underwriters by leveraging historical loan outcomes rather than opaque predictive models.

Instead of automatically approving or rejecting a loan, the system:

- Retrieves historically similar loan cases  
- Surfaces their real observed outcomes (*Repaid, Defaulted, In Progress, Fraud*)  
- Provides explainable, evidence-based insights to human decision-makers  

This approach prioritizes:

- Transparency  
- Auditability  
- Human-in-the-loop decisioning  

---

## 2. Problem Statement

Traditional credit decisioning systems often rely on:

- Black-box scoring models  
- Over-recomputation of risk  
- Limited explainability for auditors and regulators  

Additionally, real-world loan datasets suffer from:

- Outcome imbalance  
- Temporal censoring (many loans are still ongoing)  

These issues reduce trust and decision quality.

---

## 3. Solution Vision

We implement a **Decision Memory Engine** that:

- Stores historical loan applications as vectors  
- Uses similarity search to retrieve comparable past cases  
- Explains decisions using actual outcomes, not predictions  

The system acts as a **memory layer rather than a classifier**.

---

## 4. Default Demo Scenarios (Important for Evaluation)

### ✅ Default Case on Application Load (Good Case)

When the application is opened, the UI is intentionally pre-filled with a **low-risk loan profile**.

This design choice allows evaluators to immediately observe a healthy similarity-based outcome without manual configuration.

**Typical characteristics:**
- Stable income  
- Low debt-to-income ratio  
- Strong credit score  
- Reasonable loan amount and tenure  
- Salaried employment  
- Owned property  
- Practical loan purpose  

**Expected behavior:**
- Majority of *Repaid* historical cases  
- Minimal or no fraud signals  
- **Low Risk (Similarity-Based)** assessment  

This demonstrates normal system behavior under healthy conditions.

---

### ❌ Testing a High-Risk / Adverse Case (Manual Input)

To stress-test the system, evaluators can manually input the following example:

| Attribute | Value |
|--------|------|
| Monthly Income | $1,000 |
| Existing Monthly EMIs | $1,200 |
| Debt-to-Income Ratio | 1.20 |
| Loan Amount Requested | $10,000 |
| Loan Tenure (Months) | 24 |
| Credit Score | 760 |
| Applicant Age | 59 |
| Number of Dependents | 1 |
| Employment Status | Self-Employed |
| Property Ownership | Mortgaged |
| Loan Type | Auto Loan |
| Purpose of Loan | Business |

**Why this is high-risk:**
- Debt obligations exceed income  
- High financial stress (DTI > 1)  
- Business loan with uncertain cash flows  
- Older applicant with reduced flexibility  
- Mortgaged property increases exposure  

**Expected system behavior:**
- Higher proportion of *Defaulted / In-Progress* cases  
- Possible fraud signals  
- **High Risk (Similarity-Based)** assessment  

This contrast highlights the system’s reasoning capability.

---

## 5. System Architecture

```
User Input (UI)
      ↓
Feature Preprocessing
(Standardization + Encoding)
      ↓
Vector Representation
      ↓
Qdrant Vector Database
      ↓
Similarity Search (Top-K)
      ↓
Outcome Aggregation
      ↓
Explainable Decision Summary
      ↓
PDF Decision Report
```

---

## 6. Qdrant Integration (Core Component)

Qdrant is used as a **decision memory**, not a prediction engine.

**How it works:**
- Each historical loan is vectorized using:
  - Financial indicators  
  - Loan parameters  
  - Applicant attributes  
- Vectors are stored in Qdrant along with metadata:
  - Loan outcome  
  - Fraud flag  
  - Loan type and purpose  
- New applications are vectorized using the same pipeline  
- Qdrant retrieves the Top-K most similar cases  
- Outcomes are aggregated and explained  

Similarity metrics are configured at the collection level (e.g., cosine similarity).

---

## 7. Data Pipeline

### Data Preparation
- Structured loan application data  
- Numerical + categorical features selected  
- Sensitive identifiers excluded or masked  

### Temporal Adjustment
Most loans were recent and still ongoing.  
To reduce outcome bias:
- Application dates were synthetically shifted backward  
- Loan maturity was recalculated  
- Outcomes re-derived accordingly  

### Vectorization
- Numerical features: `StandardScaler`  
- Categorical features: One-Hot Encoding  
- Resulting vectors stored in Qdrant  

---

## 8. Technologies Used

| Technology | Version |
|---------|--------|
| Python | 3.10 |
| Streamlit | Latest |
| Qdrant Client | 1.7.3 |
| Scikit-learn | 1.6.1 |
| Pandas | 3.0.0 |
| NumPy | 2.4.1 |
| Plotly | Latest |
| ReportLab | Latest |

*(Exact versions listed in `requirements.txt`)*

---

## 9. Setup & Installation

### Prerequisites
- Python 3.10+  
- Qdrant Cloud account or local Qdrant instance  

### Installation
```bash
pip install -r requirements.txt
```

### Environment Variables
Create a `.env` file:
```env
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_api_key
```

### Run the App
```bash
streamlit run src/ui_app.py
```

---

## 10. Usage Example

1. Launch the Streamlit UI  
2. Review the default (low-risk) loan case  
3. Click **Analyze Loan Case**  
4. Observe:
   - Similarity-based risk assessment  
   - Outcome distribution  
   - Comparable historical cases  
5. Generate a bank-grade PDF decision report  
6. Optionally input the documented high-risk case to compare behavior  

---

## 11. Key Design Principles

- Similarity over prediction  
- Explainability by design  
- Human-in-the-loop  
- Audit-ready outputs  
- Clear risk contrast  
- Safety-first reasoning  

---

## 12. Future Enhancements

- Multimodal document embeddings (IDs, statements)  
- Feature weighting per loan type  
- Survival-analysis-aware similarity  
- Portfolio-level risk analytics  
- Governance & fairness monitoring  

---

## 13. Conclusion

**Credit Decision Memory** demonstrates how vector similarity and operational memory can support transparent, defensible, and regulator-friendly credit decisioning.

By prioritizing historical evidence over black-box prediction, the system enhances trust while preserving human judgment.
