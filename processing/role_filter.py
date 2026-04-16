"""
Role Filter - Only keeps data-related roles.
Includes entry-level/junior as long as the role is in the data field.
Rejects jobs that happen to mention "data" but aren't data roles
(e.g., "Data Entry Clerk", "Data Center Technician", "Sales with data").
"""

# Titles that qualify as data roles (even junior/entry-level)
DATA_ROLE_KEYWORDS = [
    "data engineer", "data analyst", "analytics engineer",
    "bi developer", "bi engineer", "business intelligence",
    "etl developer", "etl engineer",
    "data scientist", "data science",
    "machine learning engineer", "ml engineer",
    "big data", "data architect", "data modeler",
    "database developer", "database engineer",
    "sql developer", "data specialist",
    "reporting analyst", "analytics analyst",
    "data consultant", "data developer",
    "analytics developer", "data integration",
    "data warehouse", "data platform",
    "data operations", "dataops",
    "data ops", "analytics engineer",
    "associate data", "junior data",
    "entry level data", "data associate",
    "data intern",
]

# Titles to reject even if they contain "data"
REJECT_KEYWORDS = [
    "data entry", "data center", "data processor",
    "data clerk", "data typist", "data collection",
    "data capture", "data input",
    "master data", "product data", "clinical data coordinator",
    "sales", "account executive", "account manager",
    "recruiter", "recruiting",
    "technician", "help desk", "support specialist",
    "teacher", "tutor", "instructor",
]


def is_data_role(title: str) -> bool:
    """Check if a job title is a data-related role."""
    if not title:
        return False

    t = title.lower().strip()

    # Hard reject if title contains blacklisted keywords
    for reject in REJECT_KEYWORDS:
        if reject in t:
            return False

    # Accept if title contains any data role keyword
    for keyword in DATA_ROLE_KEYWORDS:
        if keyword in t:
            return True

    # Catch broader data/analytics titles that don't match specific patterns
    # but should still be considered data roles
    broad_patterns = ["analyst", "analytics", "data ", " data"]
    for pattern in broad_patterns:
        if pattern in t:
            # Extra safety — must not have a non-data context
            if not any(bad in t for bad in ["financial analyst", "credit analyst", "marketing analyst", "research analyst", "policy analyst"]):
                return True

    return False


def filter_data_roles(jobs: list[dict]) -> list[dict]:
    """Keep only jobs with data-related titles."""
    kept = []
    rejected = 0

    for job in jobs:
        title = job.get("title", "")
        if is_data_role(title):
            kept.append(job)
        else:
            rejected += 1

    print(f"  [RoleFilter] {len(jobs)} → {len(kept)} (rejected {rejected} non-data roles)")
    return kept
