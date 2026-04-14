"""
Jobright.ai H1B Jobs Scraper.
Scrapes the public GitHub repo: jobright-ai/Daily-H1B-Jobs-In-Tech
This repo is updated daily with verified H1B-sponsoring jobs.
"""
import re
import requests
import time
from config import APIFY_API_TOKEN


def scrape_jobright() -> list[dict]:
    """Scrape Jobright H1B jobs from their public GitHub repo."""
    print("  [Jobright] Fetching H1B jobs from GitHub repo...")

    actor_input = {
        "query": "https://github.com/jobright-ai/Daily-H1B-Jobs-In-Tech",
        "maxResults": 1,
        "outputFormats": ["markdown"],
    }

    run_url = (
        f"https://api.apify.com/v2/acts/apify~rag-web-browser/runs"
        f"?token={APIFY_API_TOKEN}"
    )

    try:
        resp = requests.post(run_url, json=actor_input, timeout=30)
        resp.raise_for_status()
        run_data = resp.json()["data"]
        run_id = run_data["id"]
        dataset_id = run_data["defaultDatasetId"]
    except Exception as e:
        print(f"  [Jobright] Failed to start actor: {e}")
        return []

    # Poll for completion
    status_url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_API_TOKEN}"
    for _ in range(60):
        time.sleep(10)
        try:
            status = requests.get(status_url, timeout=15).json()["data"]["status"]
            if status == "SUCCEEDED":
                break
            elif status in ("FAILED", "ABORTED", "TIMED-OUT"):
                print(f"  [Jobright] Run {status}")
                return []
        except Exception:
            continue
    else:
        print("  [Jobright] Timed out waiting for results")
        return []

    # Fetch results
    items_url = (
        f"https://api.apify.com/v2/datasets/{dataset_id}/items"
        f"?token={APIFY_API_TOKEN}&format=json"
    )
    try:
        items = requests.get(items_url, timeout=30).json()
    except Exception as e:
        print(f"  [Jobright] Failed to fetch results: {e}")
        return []

    jobs = []
    for item in items:
        markdown = item.get("markdown", item.get("text", ""))
        extracted = _parse_jobright_table(markdown)
        jobs.extend(extracted)

    print(f"  [Jobright] Found {len(jobs)} H1B jobs")
    return jobs


def _parse_jobright_table(markdown: str) -> list[dict]:
    """Parse the tab-separated table from Jobright GitHub repo."""
    jobs = []
    lines = markdown.split("\n")

    data_keywords = [
        "data", "analyst", "analytics", "etl", "pipeline",
        "warehouse", "bi ", "business intelligence", "scientist"
    ]

    for line in lines:
        # Skip non-data lines
        if "\tapply\t" not in line:
            continue

        parts = [p.strip() for p in line.split("\t")]
        if len(parts) < 7:
            continue

        company = parts[0].strip("↳ ")
        title = parts[1] if len(parts) > 1 else ""
        level = parts[2] if len(parts) > 2 else ""
        location = parts[3] if len(parts) > 3 else ""
        h1b_status = parts[4] if len(parts) > 4 else ""
        date_posted = parts[6] if len(parts) > 6 else ""

        title_lower = title.lower()
        if not any(kw in title_lower for kw in data_keywords):
            continue

        sponsorship = "Yes (H1B explicit)" if "🏅" in h1b_status else "Yes (H1B history)"

        # Build the jobright search URL since apply links aren't in text format
        apply_url = f"https://jobright.ai/jobs?title={title.replace(' ', '+')}&company={company.replace(' ', '+')}"

        jobs.append({
            "title": title,
            "company": company,
            "location": location,
            "apply_link": apply_url,
            "posted_time": date_posted,
            "applicants": "Unknown",
            "description": f"Level: {level}. H1B sponsorship verified.",
            "source": "Jobright (H1B)",
            "visa_sponsorship": sponsorship,
        })

    return jobs
