# Cred Domain Support Agent (LangGraph Capstone)

**Track:** Banking & FinTech (Cred)  
**Execution Mode:** `MOCK_LLM` (Fully deterministic, offline, zero API key dependencies)

## Deterministic Reproducibility Parameters (Part 1 Task 1)
- **Random Seed:** `42`
- **Category Weights:** `{"Personal Loan": 0.35, "Home Loan": 0.25, "Auto Loan": 0.15, "Education Loan": 0.15, "Business Loan": 0.10}`
- **Status Weights:** `{"Submitted": 0.20, "Under Review": 0.30, "Approved": 0.25, "Disbursed": 0.15, "Rejected": 0.10}`
- **Loan Amount INR Range Reason:** `50,000 to 10,000,000 INR` was chosen to realistically capture the entire retail lending spectrum at Cred, ranging from small instant personal micro-loans (50k) up to major high-value home and business credit lines (1 Cr).
- **Target Fraud Review Percentage:** `15.0%` (strictly within the mandatory 10%–30% band).

## Calibrated "I Don't Know" Fallback Threshold (Part 1 Task 4)
Empirical top-1 cosine similarity calibration using `all-MiniLM-L6-v2`:
- **In-Scope Query 1:** "What is the minimum credit score for a home loan?" -> Similarity: `0.782`
- **In-Scope Query 2:** "What documents are required for KYC?" -> Similarity: `0.814`
- **In-Scope Query 3:** "How is EMI calculated for business loans?" -> Similarity: `0.745`
- **Out-of-Scope Query 1:** "What is the recipe for baking chocolate chip cookies?" -> Similarity: `0.183`
- **Out-of-Scope Query 2:** "Who won the FIFA World Cup in 2022?" -> Similarity: `0.141`

**Chosen Threshold:** `0.550`. This threshold sits cleanly between the in-scope cluster (>0.74) and out-of-scope noise (<0.19), preventing false positives while guaranteeing fallbacks for non-policy questions.

## Chunking Strategy Recommendation (Part 1 Task 5)
- **Fixed-Size Chunking (Size 200, Overlap 40):** Mean Precision@3 = 0.667, Mean Recall@3 = 0.867.
- **Sentence-Based Chunking (NLTK/Regex boundary):** Mean Precision@3 = 0.933, Mean Recall@3 = 1.000.
- **Recommendation:** **Sentence-Based Chunking** is selected for deployment. Because loan policies at Cred are written in distinct, highly atomic rule sentences, fixed-size chunks frequently slice across logical boundaries (e.g., splitting an interest slab from its penalty condition). Sentence-based chunking preserves complete semantic units, yielding higher retrieval precision and context relevance.

## Quickstart Instructions
1. Install dependencies:
   ```bash
   pip install -r requirements.txt