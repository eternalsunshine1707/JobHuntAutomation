"""
LinkedIn Jobs Scraper using Apify Actor: curious_coder/linkedin-jobs-scraper
"""
import requests
import time
from config import APIFY_API_TOKEN, MAX_JOBS_PER_PLATFORM


def scrape_linkedin(job_title: str, location: str = "United States") -> list[dict]:
    """Scrape LinkedIn jobs for a given title and location."""
    print(f"  [LinkedIn] Searching: {job_title} in {location}...")

    search_url = (
        f"https://www.linkedin.com/jobs/search/"
        f"?keywords={job_title.replace(' ', '%20')}"
        f"&location={location.replace(' ', '%20')}"
        f"&f_TPR=r86400"  # last 24 hours
        f"&position=1&pageNum=0"
    )

    actor_input = {
        "urls": [search_url],
        "count": MAX_JOBS_PER_PLATFORM,
        "scrapeCompany": False,
    }

    run_url = (
        f"https://api.apify.com/v2/acts/curious_coder~linkedin-jobs-scraper/runs"
        f"?token={APIFY_API_TOKEN}"
    )

    try:
        resp = requests.post(run_url, json=actor_input, timeout=30)
        resp.raise_for_status()
        run_data = resp.json()["data"]
        run_id = run_data["id"]
        dataset_id = run_data["defaultDatasetId"]
    except Exception as e:
        print(f"  [LinkedIn] Failed to start actor: {e}")
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
                print(f"  [LinkedIn] Run {status}")
                return []
        except Exception:
            continue
    else:
        print("  [LinkedIn] Timed out waiting for results")
        return []

    # Fetch results
    items_url = (
        f"https://api.apify.com/v2/datasets/{dataset_id}/items"
        f"?token={APIFY_API_TOKEN}&format=json"
    )
    try:
        items = requests.get(items_url, timeout=30).json()
    except Exception as e:
        print(f"  [LinkedIn] Failed to fetch results: {e}")
        return []

    jobs = []
    for item in items:
        # LinkedIn returns 'link' as the job URL, 'companyName', 'descriptionText'
        apply_link = item.get("link", "")
        posted_raw = item.get("postedAt", item.get("postedAtTimestamp", "Unknown"))
        applicants = item.get("applicantsCount", "Unknown")
        description = item.get("descriptionText", item.get("description", ""))
        if isinstance(description, dict):
            description = description.get("text", "")

        job = {
            "title": item.get("title", ""),
            "company": item.get("companyName", ""),
            "location": item.get("location", ""),
            "apply_link": apply_link,
            "posted_time": str(posted_raw),
            "applicants": str(applicants) if applicants else "Unknown",
            "description": str(description)[:500],
            "source": "LinkedIn",
        }
        if job["title"] and job["company"] and job["apply_link"]:
            jobs.append(job)

    print(f"  [LinkedIn] Found {len(jobs)} jobs for '{job_title}'")
    return jobs
