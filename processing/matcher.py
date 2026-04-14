"""
Job Matcher - Scores and filters jobs based on skill relevance to resume.
Also detects visa sponsorship likelihood.
"""
from config import CORE_SKILLS, VISA_POSITIVE, VISA_NEGATIVE


# Only show this many jobs per email — quality over quantity
MAX_JOBS_PER_EMAIL = 20
MIN_MATCH_SCORE = 30  # Drop jobs scoring below this


def score_job(job: dict) -> int:
    """Score a job 0-100 based on how well it matches the resume skills."""
    text = f"{job.get('title', '')} {job.get('description', '')}".lower()
    title = job.get("title", "").lower()

    # If no description at all, score based on title alone
    if not text.strip():
        return 10

    # Count skill matches
    matches = sum(1 for skill in CORE_SKILLS if skill in text)
    score = min(100, int((matches / len(CORE_SKILLS)) * 300))

    # Bonus for exact title match
    title_keywords = ["data engineer", "data analyst", "analytics engineer", "bi developer", "etl developer"]
    if any(kw in title for kw in title_keywords):
        score = min(100, score + 15)

    # Penalty for senior/staff/principal/director roles (less likely to get interview)
    seniority_flags = ["staff ", "principal", "director", "vp ", "distinguished", "lead architect"]
    if any(flag in title for flag in seniority_flags):
        score = max(0, score - 20)

    return max(0, score)


def detect_visa_sponsorship(job: dict) -> str:
    """Detect visa sponsorship status from job description."""
    # If already set by scraper (e.g., Jobright)
    if job.get("visa_sponsorship"):
        return job["visa_sponsorship"]

    text = f"{job.get('title', '')} {job.get('description', '')}".lower()
    if not text.strip():
        return "Unknown"

    for neg in VISA_NEGATIVE:
        if neg in text:
            return "No"

    for pos in VISA_POSITIVE:
        if pos in text:
            return "Yes"

    # Check company-level H1B sponsorship history (known sponsors)
    company = job.get("company", "").lower()
    known_sponsors = [
        "capital one", "google", "amazon", "microsoft", "meta", "apple",
        "deloitte", "pwc", "accenture", "infosys", "tcs", "wipro",
        "jpmorgan", "goldman sachs", "morgan stanley", "bloomberg",
        "salesforce", "oracle", "ibm", "intel", "nvidia", "adobe",
        "uber", "lyft", "airbnb", "stripe", "palantir", "snowflake",
        "databricks", "datadog", "splunk", "confluent", "mongodb",
        "elastic", "twilio", "shopify", "walmart", "target",
        "ford", "gm", "boeing", "lockheed", "raytheon",
        "unitedhealth", "cigna", "anthem", "humana",
        "bae systems", "northrop", "general dynamics",
    ]
    if any(sponsor in company for sponsor in known_sponsors):
        return "Yes (H1B history)"

    return "Unknown"


def filter_and_score_jobs(jobs: list[dict]) -> list[dict]:
    """Score, filter, and rank jobs. Returns only the top matches."""
    scored = []
    for job in jobs:
        # Skip jobs without a valid apply link
        link = job.get("apply_link", "")
        if not link or not link.startswith("http"):
            continue

        job["match_score"] = score_job(job)
        job["visa_sponsorship"] = detect_visa_sponsorship(job)

        # Skip jobs that explicitly say "No" to sponsorship
        if job["visa_sponsorship"] == "No":
            continue

        # Skip jobs below minimum score
        if job["match_score"] < MIN_MATCH_SCORE:
            continue

        scored.append(job)

    # Sort by match score descending
    scored.sort(key=lambda x: x["match_score"], reverse=True)

    # Cap at top N
    result = scored[:MAX_JOBS_PER_EMAIL]
    print(f"  [Matcher] {len(jobs)} raw → {len(scored)} passed filters → showing top {len(result)}")
    return result
