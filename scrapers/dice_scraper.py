"""
Dice.com Jobs Scraper using Apify Actor: shahidirfan/Dice-Job-Scraper
"""
import requests
import time
from config import APIFY_API_TOKEN, MAX_JOBS_PER_PLATFORM


def scrape_dice(job_title: str, location: str = "United States") -> list[dict]:
    """Scrape Dice.com jobs for a given title and location."""
    print(f"  [Dice] Searching: {job_title} in {location}...")

    actor_input = {
        "keyword": job_title,
        "location": location,
        "maxItems": MAX_JOBS_PER_PLATFORM,
        "postedDate": "ONE",  # last 24 hours
    }

    run_url = (
        f"https://api.apify.com/v2/acts/shahidirfan~Dice-Job-Scraper/runs"
        f"?token={APIFY_API_TOKEN}"
    )

    try:
        resp = requests.post(run_url, json=actor_input, timeout=30)
        resp.raise_for_status()
        run_data = resp.json()["data"]
        run_id = run_data["id"]
        dataset_id = run_data["defaultDatasetId"]
    except Exception as e:
        print(f"  [Dice] Failed to start actor: {e}")
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
                print(f"  [Dice] Run {status}")
                return []
        except Exception:
            continue
    else:
        print("  [Dice] Timed out waiting for results")
        return []

    # Fetch results
    items_url = (
        f"https://api.apify.com/v2/datasets/{dataset_id}/items"
        f"?token={APIFY_API_TOKEN}&format=json"
    )
    try:
        items = requests.get(items_url, timeout=30).json()
    except Exception as e:
        print(f"  [Dice] Failed to fetch results: {e}")
        return []

    jobs = []
    for item in items:
        job = {
            "title": item.get("title", item.get("jobTitle", "")),
            "company": item.get("companyName", item.get("company", "")),
            "location": item.get("location", item.get("jobLocation", "")),
            "apply_link": item.get("url", item.get("jobUrl", item.get("link", ""))),
            "posted_time": item.get("postedDate", item.get("datePosted", "Unknown")),
            "applicants": item.get("applicantsCount", "Unknown"),
            "description": item.get("description", item.get("jobDescription", "")),
            "source": "Dice",
        }
        if job["title"] and job["company"]:
            jobs.append(job)

    print(f"  [Dice] Found {len(jobs)} jobs for '{job_title}'")
    return jobs
