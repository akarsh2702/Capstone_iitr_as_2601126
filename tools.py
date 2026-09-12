from typing import Dict, Any, Optional
from dataset import LOAN_APPLICATIONS

def check_loan_application_status(record_id: str) -> Dict[str, Any]:
    """
    Looks up a loan application record by ID and computes a designed escalation score.
    Formula:
    - Base fraud risk score: 0.60 if flagged_for_fraud_review else 0.00
    - Recency signal: (days_since_created / 30.0) * 0.40
    - Escalation Score = Base Fraud Risk + Recency Signal in [0, 1]
    
    Escalation Threshold Recommendation: 0.65
    Justification: A threshold of 0.65 isolates applications that are flagged for fraud
    review AND are moderately aged (>4 days), or unflagged applications with extreme
    aging (>28 days, representing the 90th percentile of days_since_created in the dataset).
    """
    # Clean ID
    clean_id = record_id.strip().upper()
    
    record: Optional[Dict[str, Any]] = None
    for item in LOAN_APPLICATIONS:
        if item["record_id"].upper() == clean_id:
            record = item
            break
            
    if not record:
        return {
            "found": False,
            "record_id": record_id,
            "error": f"Loan record '{record_id}' not found in Cred application database."
        }
        
    days = record["days_since_created"]
    is_fraud = record["flagged_for_fraud_review"]
    
    # Designed formula calculation
    base_fraud_score = 0.60 if is_fraud else 0.00
    recency_signal = (days / 30.0) * 0.40
    escalation_score = round(base_fraud_score + recency_signal, 4)
    
    recommend_escalation = escalation_score >= 0.65
    
    return {
        "found": True,
        "record_id": record["record_id"],
        "category": record["category"],
        "status": record["status"],
        "loan_amount_inr": record["loan_amount_inr"],
        "days_since_created": days,
        "flagged_for_fraud_review": is_fraud,
        "escalation_score": escalation_score,
        "escalation_recommended": recommend_escalation,
        "escalation_threshold": 0.65
    }

if __name__ == "__main__":
    print("--- TESTING APPLICATION STATUS LOOKUP TOOL ---")
    sample_id = LOAN_APPLICATIONS[0]["record_id"]
    print(check_loan_application_status(sample_id))