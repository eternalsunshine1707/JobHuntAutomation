"""
Built In Jobs Scraper using Apify RAG Web Browser.
Built In doesn't have a dedicated Apify actor, so we scrape via web browser.
"""
import re
import requests
import time
from config import APIFY_API_TOKEN, MAX_JOBS_PER_PLATFORM


def scrape_builtin(job_title: str, location: str = "United States") -> list[dict]:
    """Scrape Built In jobs using Apify RAG web browser."""
    print(f"  [BuiltIn] Searching: {job_title}...")

    query = f"site:builtin.com {job_title} jobs posted today"

    actor_input = {
        "query": query,
        "maxResults": 5,
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
        markdown = item.get("markdown", item.get("text", ""))
        page_url = item.get("url", item.get("crawl", {}).get("requestUrl", ""))

        # Extract job-like entries from the markdown
        extracted = _parse_builtin_markdown(markdown, page_url)
        jobs.extend(extracted)

    # Deduplicate within BuiltIn results
    seen = set()
    unique_jobs = []
    for j in jobs:
        key = f"{j['company']}|{j['title']}"
        if key not in seen:
            seen.add(key)
            unique_jobs.append(j)

    print(f"  [BuiltIn] Found {len(unique_jobs)} jobs for '{job_title}'")
    return unique_jobs[:MAX_JOBS_PER_PLATFORM]


def _parse_builtin_markdown(markdown: str, page_url: str) -> list[dict]:
    """Parse Built In page markdown to extract job listings."""
    jobs = []
    lines = markdown.split("\n")

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Look for patterns that indicate a job listing
        # Built In typically shows: Company name, Job title, location, skills
        if any(kw in line.lower() for kw in ["data engineer", "data analyst", "business analyst", "analytics engineer"]):
            title = line.strip("#*[] ")
            company = ""
            location = ""

            # Look around for company and location info
            for offset in range(-3, 4):
                if 0 <= i + offset < len(lines):
                    nearby = lines[i + offset].strip()
                    # Company names are often on nearby lines
                    if nearby and nearby != line and not nearby.startswith("Top Skills"):
                        if not company and len(nearby) < 60 and not any(
                            kw in nearby.lower() for kw in ["skills", "top", "apply", "use our", "search"]
                        ):
                            company = nearby.strip("#*[] •·")
                        # Location patterns
                        if any(loc in nearby for loc in [", CA", ", NY", ", TX", ", WA", ", VA", ", DC", "Remote"]):
                            location = nearby.strip("#*[] •·")

            if title and len(title) > 5:
                jobs.append({
                    "title": title[:100],
                    "company": company[:80] if company else "See listing",
                    "location": location if location else "USA",
                    "apply_link": page_url,
                    "posted_time": "Recent",
                    "applicants": "Unknown",
                    "description": "",
                    "source": "Built In",
                })
        i += 1

    return jobs
