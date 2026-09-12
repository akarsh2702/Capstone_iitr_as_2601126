from typing import List, Dict

KNOWLEDGE_BASE_DOCUMENTS: List[Dict[str, str]] = [
    {
        "doc_id": "DOC-001",
        "topic": "loan_eligibility_criteria",
        "title": "Loan Eligibility Criteria by Loan Type",
        "content": "Personal loans require a minimum monthly net income of INR 35,000 and at least 21 years of age. Home loans require a minimum continuous employment history of 2 years and a baseline CIBIL score of 720. Business loans necessitate an operational vintage of at least 3 years with audited financial statements proving profitability. Auto loans are granted up to 85% of the vehicle ex-showroom price subject to income verification."
    },
    {
        "doc_id": "DOC-002",
        "topic": "emi_calculation_rules",
        "title": "EMI Calculation Rules and Methods",
        "content": "Equated Monthly Installments (EMI) are computed using the reducing-balance method where interest is charged only on the outstanding principal amount. The standard formula applies principal, monthly interest rate, and tenure in months. Prepayment directly reduces the remaining loan tenure or reduces subsequent EMI amounts based on member preference. Interest calculations accrue daily and post to the account on the final calendar day of each month."
    },
    {
        "doc_id": "DOC-003",
        "topic": "credit_card_fee_structure",
        "title": "Credit Card Fee Structure and Charges",
        "content": "Cred credit cards carry an annual membership fee ranging from INR 500 to INR 4,999 waived upon achieving annual spend thresholds. Late payment charges accrue at a tiered rate based on outstanding statement balances exceeding INR 1,000. Cash advance fees are levied at 2.5% of the withdrawn amount subject to a minimum charge of INR 500. Foreign currency markup fees are set at 3.5% for standard cards and 1.5% for premium metal tiers."
    },
    {
        "doc_id": "DOC-004",
        "topic": "kyc_document_requirements",
        "title": "KYC Document Requirements for Verification",
        "content": "Identity verification requires a valid Passport, Voter ID, Driving License, or Aadhaar number. Address proof must be substantiated using utility bills less than 3 months old, registered rent agreements, or bank statements. Financial verification requires 6 months of bank account statements and the last 3 months of salary slips or Form 16. Permanent Account Number (PAN) submission is mandatory for all credit facilities exceeding INR 50,000."
    },
    {
        "doc_id": "DOC-005",
        "topic": "fraud_dispute_resolution",
        "title": "Fraud Dispute Resolution Process",
        "content": "Unauthorized transactions must be reported within 3 business days to qualify for zero customer liability protection. Members can raise a dispute directly through the Cred mobile application or by notifying dedicated support staff. Temporary shadow credit is credited to the account within 7 working days pending formal investigation. Final dispute resolution and merchant chargeback claims conclude within 45 calendar days of initial reporting."
    },
    {
        "doc_id": "DOC-006",
        "topic": "account_closure_process",
        "title": "Account Closure Process and Requirements",
        "content": "Loan or credit account closure requires complete liquidation of outstanding principal, accrued interest, and pending charges. A formal No Dues Certificate (NDC) is generated and dispatched within 10 working days after full settlement. Hypothecation on vehicle loans or property liens are released concurrently with issuing NOC documentation. Accounts with active pending disputes or unsettled EMI bounces cannot initiate closure proceedings."
    },
    {
        "doc_id": "DOC-007",
        "topic": "interest_rate_slabs",
        "title": "Interest Rate Slabs Across Loan Products",
        "content": "Personal loan interest rates range between 10.5% and 18.0% per annum determined by member risk profiles. Home loan floating rates are benchmarked to the RBI Repo Rate plus a spread between 2.15% and 3.50%. Business loan interest rates operate on fixed slabs between 14.0% and 22.0% depending on business turnover and cash flow stability. Auto loan rates are fixed between 8.75% and 11.25% across 36 to 84 month tenures."
    },
    {
        "doc_id": "DOC-008",
        "topic": "prepayment_penalty_rules",
        "title": "Prepayment Penalty Rules and Limits",
        "content": "Floating rate home loans and individual personal loans carry zero prepayment or foreclosure charges under RBI guidelines. Fixed-rate business loans incur a 3% foreclosure fee if settled within the first 12 months of tenure. Part-prepayments are allowed up to 25% of the outstanding principal balance per financial year without penalty. Written notification 15 days prior to prepayment is required for commercial credit lines."
    },
    {
        "doc_id": "DOC-009",
        "topic": "minimum_balance_requirements",
        "title": "Minimum Balance Requirements and Penalty Slabs",
        "content": "Cred Salary Savings accounts maintain a zero minimum average monthly balance (AMB) requirement. Standard savings accounts require an AMB of INR 10,000 in metro locations and INR 5,000 in semi-urban branches. Non-maintenance of AMB attracts a tiered penalty of 5% of the shortfall capped at INR 500 per month. Premium wealth management accounts require a combined relationship value of INR 5,00,000 across savings and investments."
    },
    {
        "doc_id": "DOC-010",
        "topic": "credit_score_impact_factors",
        "title": "Credit Score Impact Factors and Calculation",
        "content": "Payment history accounts for 35% of the total CIBIL score calculation, making on-time EMI payment critical. Credit utilization ratio contributes 30% to the score, and keeping utilization below 30% is strongly advised. Length of credit history and mix of secured versus unsecured credit account for 25% of score weightage. Multiple hard credit enquiries within short durations reduce credit scores temporarily by 5 to 15 points."
    },
    {
        "doc_id": "DOC-011",
        "topic": "joint_account_rules",
        "title": "Joint Account Rules and Operations",
        "content": "Joint loan applications allow co-applicants including spouses, parents, or lineal co-borrowers to pool income for higher eligibility. Primary financial liability rests equally on all co-borrowers regardless of designated repayment arrangements. Primary applicants must maintain active KYC status, and all joint holders must sign loan agreement mandates. Tax exemption benefits under Section 24 and 80C are proportionally shareable among co-borrowers."
    },
    {
        "doc_id": "DOC-012",
        "topic": "nri_account_eligibility",
        "title": "NRI Account Eligibility and Documentation",
        "content": "Non-Resident Indians (NRIs) and Persons of Indian Origin (PIOs) are eligible for home and personal loans against NRE/NRO accounts. Overseas income verification requires notarized employment contracts, last 6 months overseas bank statements, and tax returns. Power of Attorney (POA) must be granted to an Indian resident relative for local document execution. Loan repayments must originate directly from NRE or NRO banking channels in Indian Rupees."
    }
]