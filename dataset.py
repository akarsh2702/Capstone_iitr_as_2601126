import random
import json
from typing import List, Dict, Any

SEED = 42
TOTAL_RECORDS = 50

CATEGORY_WEIGHTS = {
    "Personal Loan": 0.35,
    "Home Loan": 0.25,
    "Auto Loan": 0.15,
    "Education Loan": 0.15,
    "Business Loan": 0.10
}

STATUS_WEIGHTS = {
    "Submitted": 0.20,
    "Under Review": 0.30,
    "Approved": 0.25,
    "Disbursed": 0.15,
    "Rejected": 0.10
}

def generate_loan_dataset(seed: int = SEED, total: int = TOTAL_RECORDS) -> List[Dict[str, Any]]:
    random.seed(seed)
    categories = list(CATEGORY_WEIGHTS.keys())
    cat_weights = list(CATEGORY_WEIGHTS.values())
    
    statuses = list(STATUS_WEIGHTS.keys())
    stat_weights = list(STATUS_WEIGHTS.values())
    
    dataset = []
    
    for i in range(1, total + 1):
        record_id = f"CRD-LN-{1000 + i}"
        category = random.choices(categories, weights=cat_weights, k=1)[0]
        status = random.choices(statuses, weights=stat_weights, k=1)[0]
        
        # Loan amounts INR range: 50,000 to 10,000,000
        if category == "Personal Loan":
            amount = random.randint(50, 150) * 10000
        elif category == "Home Loan":
            amount = random.randint(250, 1000) * 10000
        elif category == "Auto Loan":
            amount = random.randint(100, 300) * 10000
        elif category == "Education Loan":
            amount = random.randint(50, 400) * 10000
        else: # Business Loan
            amount = random.randint(200, 800) * 10000
            
        days_since_created = random.randint(0, 30)
        
        # Controlled fraud review generation targeting ~15%
        # High-risk trigger condition + random baseline
        fraud_prob = 0.10
        if days_since_created > 20 and status in ["Under Review", "Submitted"]:
            fraud_prob += 0.25
        if amount > 5000000:
            fraud_prob += 0.15
            
        flagged_for_fraud = random.random() < fraud_prob
        
        dataset.append({
            "record_id": record_id,
            "category": category,
            "status": status,
            "loan_amount_inr": amount,
            "days_since_created": days_since_created,
            "flagged_for_fraud_review": flagged_for_fraud
        })
        
    return dataset

def validate_dataset(dataset: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(dataset)
    cat_counts = {}
    stat_counts = {}
    fraud_count = 0
    
    for r in dataset:
        cat_counts[r["category"]] = cat_counts.get(r["category"], 0) + 1
        stat_counts[r["status"]] = stat_counts.get(r["status"], 0) + 1
        if r["flagged_for_fraud_review"]:
            fraud_count += 1
            
    fraud_pct = (fraud_count / total) * 100.0
    
    # Validation checks
    assert total >= 40, f"Expected >=40 records, got {total}"
    for cat in CATEGORY_WEIGHTS.keys():
        assert cat_counts.get(cat, 0) >= 3, f"Category {cat} has less than 3 records: {cat_counts.get(cat, 0)}"
    for stat in STATUS_WEIGHTS.keys():
        assert stat_counts.get(stat, 0) >= 1, f"Status {stat} has less than 1 record: {stat_counts.get(stat, 0)}"
    assert 10.0 <= fraud_pct <= 30.0, f"Fraud % {fraud_pct:.2f}% outside allowed 10%-30% range!"
    
    stats = {
        "total_records": total,
        "category_counts": cat_counts,
        "status_counts": stat_counts,
        "fraud_flagged_count": fraud_count,
        "fraud_flagged_percentage": round(fraud_pct, 2)
    }
    return stats

LOAN_APPLICATIONS = generate_loan_dataset()

if __name__ == "__main__":
    stats = validate_dataset(LOAN_APPLICATIONS)
    print("--- LOAN DATASET GENERATION & VALIDATION REPORT ---")
    print(json.dumps(stats, indent=2))