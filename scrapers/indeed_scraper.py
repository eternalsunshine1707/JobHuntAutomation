"""
Indeed Jobs Scraper using Apify Actor: valig/indeed-jobs-scraper
"""
import requests
import time
from config import APIFY_API_TOKEN, MAX_JOBS_PER_PLATFORM


def scrape_indeed(job_title: str, location: str = "United States") -> list[dict]:
    """Scrape Indeed jobs for a given title and location."""
    print(f"  [Indeed] Searching: {job_title} in {location}...")

    actor_input = {
        "title": job_title,
        "location": location,
        "country": "us",
        "limit": MAX_JOBS_PER_PLATFORM,
        "datePosted": "1",  # last 24 hours
    }

    run_url = (
        f"https://api.apify.com/v2/acts/valig~indeed-jobs-scraper/runs"
        f"?token={APIFY_API_TOKEN}"
    )

    try:
        resp = requests.post(run_url, json=actor_input, timeout=30)
        resp.raise_for_status()
        run_data = resp.json()["data"]
        run_id = run_data["id"]
        dataset_id = run_data["defaultDatasetId"]
    except Exception as e:
        print(f"  [Indeed] Failed to start actor: {e}")
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
                print(f"  [Indeed] Run {status}")
                return []
        except Exception:
            continue
    else:
        print("  [Indeed] Timed out waiting for results")
        return []

    # Fetch results
    items_url = (
        f"https://api.apify.com/v2/datasets/{dataset_id}/items"
        f"?token={APIFY_API_TOKEN}&format=json"
    )
    try:
        items = requests.get(items_url, timeout=30).json()
    except Exception as e:
        print(f"  [Indeed] Failed to fetch results: {e}")
        return []

    jobs = []
    for item in items:
        # Extract nested fields
        loc = item.get("location", {})
        if isinstance(loc, dict):
            city = loc.get("city", "")
            state = loc.get("admin1Code", "")
            location_str = f"{city}, {state}".strip(", ") if city else "USA"
        else:
            location_str = str(loc)

        employer = item.get("employer", {})
        company_name = employer.get("name", "") if isinstance(employer, dict) else ""

        desc = item.get("description", {})
        desc_text = desc.get("text", "") if isinstance(desc, dict) else str(desc)

        # Get the actual job application URL (external company page)
        apply_link = item.get("jobUrl", item.get("url", ""))

        # Parse posting time
        posted = item.get("datePublished", item.get("dateOnIndeed", "Unknown"))

        # Salary info
        salary = item.get("baseSalary", {})
        salary_str = ""
        if isinstance(salary, dict) and salary.get("min"):
            salary_str = f"${int(salary['min']):,} - ${int(salary.get('max', salary['min'])):,}/{salary.get('unitOfWork', 'YEAR')}"

        job = {
            "title": item.get("title", ""),
            "company": company_name,
            "location": location_str,
            "apply_link": apply_link,
            "posted_time": posted,
            "applicants": "Unknown",
            "description": desc_text[:500],
            "salary": salary_str,
            "source": "Indeed",
        }
        if job["title"] and job["company"]:
            jobs.append(job)

    print(f"  [Indeed] Found {len(jobs)} jobs for '{job_title}'")
    return jobs
