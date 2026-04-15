"""
Job Matcher - Scores and filters jobs based on skill relevance to resume.
Also detects visa sponsorship likelihood.
"""
from config import CORE_SKILLS, VISA_POSITIVE, VISA_NEGATIVE


def score_job(job: dict) -> str:
    """Score a job as Great Match, Good Match, or Fair Match based on resume skills."""
    text = f"{job.get('title', '')} {job.get('description', '')}".lower()
    title = job.get("title", "").lower()

    if not text.strip():
        return "Fair Match"

    matches = sum(1 for skill in CORE_SKILLS if skill in text)
    ratio = matches / len(CORE_SKILLS)

    if ratio >= 0.15:
        return "Great Match"
    elif ratio >= 0.07:
        return "Good Match"
    else:
        return "Fair Match"


def detect_visa_sponsorship(job: dict) -> str:
    """Detect visa sponsorship status from job description."""
    # If already set by scraper (e.g., Jobright or Dice)
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
    """Score, rank, and filter jobs. Removes jobs that clearly won't sponsor."""
    scored = []
    removed_no_link = 0
    removed_no_sponsor = 0

    for job in jobs:
        # Skip jobs with completely empty apply link
        link = job.get("apply_link", "").strip()
        if not link:
            removed_no_link += 1
            continue

        job["match_score"] = score_job(job)
        job["visa_sponsorship"] = detect_visa_sponsorship(job)

        # Remove jobs that explicitly say No to sponsorship
        if job["visa_sponsorship"] == "No":
            removed_no_sponsor += 1
            continue

        scored.append(job)

    # Sort: Great Match first, then Good Match, then Fair Match
    sort_order = {"Great Match": 0, "Good Match": 1, "Fair Match": 2}
    scored.sort(key=lambda x: sort_order.get(x["match_score"], 3))

    print(f"  [Matcher] {len(jobs)} raw → removed {removed_no_link} (no link), {removed_no_sponsor} (no sponsorship) → {len(scored)} remaining")
    return scored
