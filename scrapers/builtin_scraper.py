"""
Built In Jobs Scraper using Apify Actor: easyapi/builtin-jobs-scraper
Tested and verified — returns jobUrl, companyName, jobTitle, salary, skills.
"""
import requests
import time
from config import APIFY_API_TOKEN, MAX_JOBS_PER_PLATFORM


def scrape_builtin(job_title: str, location: str = "United States") -> list[dict]:
    """Scrape Built In jobs using the dedicated Apify actor."""
    print(f"  [BuiltIn] Searching: {job_title}...")

    query = job_title.replace(" ", "+")
    search_url = f"https://builtin.com/jobs/remote/hybrid/office?search={query}"

    actor_input = {
        "searchUrls": [search_url],
        "maxItems": MAX_JOBS_PER_PLATFORM,
    }

    run_url = (
        f"https://api.apify.com/v2/acts/easyapi~builtin-jobs-scraper/runs"
        f"?token={APIFY_API_TOKEN}"
    )

    try:
        resp = requests.post(run_url, json=actor_input, timeout=30)
        resp.raise_for_status()
        run_data = resp.json()["data"]
        run_id = run_data["id"]
        dataset_id = run_data["defaultDatasetId"]
    except Exception as e:
        print(f"  [BuiltIn] Failed to start actor: {e}")
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
                print(f"  [BuiltIn] Run {status}")
                return []
        except Exception:
            continue
    else:
        print("  [BuiltIn] Timed out waiting for results")
        return []

    # Fetch results
    items_url = (
        f"https://api.apify.com/v2/datasets/{dataset_id}/items"
        f"?token={APIFY_API_TOKEN}&format=json"
    )
    try:
        items = requests.get(items_url, timeout=30).json()
    except Exception as e:
        print(f"  [BuiltIn] Failed to fetch results: {e}")
        return []

    jobs = []
    for item in items:
        # jobUrl is relative like "/job/data-engineer/8820480"
        job_url = item.get("jobUrl", "")
        if job_url and not job_url.startswith("http"):
            job_url = f"https://builtin.com{job_url}"

        # workLocation is nested: {"type": "Hybrid", "locations": ["Chicago, IL"]}
        work_loc = item.get("workLocation", {})
        if isinstance(work_loc, dict):
            locs = work_loc.get("locations", [])
            if isinstance(locs, list):
                location_str = ", ".join(locs[:3]) if locs else "USA"
            else:
                location_str = str(locs)
            loc_type = work_loc.get("type", "")
            if loc_type:
                location_str = f"{location_str} ({loc_type})"
        else:
            location_str = "USA"

        skills = item.get("skills", "")
        description = item.get("description", "")
        salary = item.get("salary", "")

        job = {
            "title": item.get("jobTitle", ""),
            "company": item.get("companyName", ""),
            "location": location_str,
            "apply_link": job_url,
            "posted_time": item.get("postDate", "Recent"),
            "applicants": "Unknown",
            "description": f"{description} Skills: {skills}" if skills else description,
            "salary": salary,
            "source": "Built In",
        }
        if job["title"] and job["company"] and job["apply_link"]:
            jobs.append(job)

    print(f"  [BuiltIn] Found {len(jobs)} jobs for '{job_title}'")
    return jobs
