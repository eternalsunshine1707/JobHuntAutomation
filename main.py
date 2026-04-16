"""
Job Hunt Automation Pipeline — Main Orchestrator

Scrapes jobs from LinkedIn, Indeed, and Dice.
Filters to US-only, data-related roles, posted since last run.
Scores by skill match, removes visa-unfriendly postings, and emails the results.
"""
import sys
import json
import os
from datetime import datetime, timezone, timedelta
from config import JOB_TITLES, LAST_RUN_FILE
from scrapers import scrape_linkedin, scrape_indeed, scrape_dice
from processing import filter_and_score_jobs, deduplicate_jobs
from processing.time_filter import filter_by_last_run, save_current_run_timestamp, get_last_run_time
from processing.location_filter import filter_us_only
from processing.role_filter import filter_data_roles
from output import generate_excel
from notify import send_email

EST = timezone(timedelta(hours=-4))


def run_pipeline():
    """Execute the full job scraping pipeline."""
    start = datetime.now(EST)
    print(f"\n{'='*60}")
    print(f"  JOB HUNT AUTOMATION PIPELINE")
    print(f"  Started: {start.strftime('%B %d, %Y at %I:%M %p EST')}")
    print(f"{'='*60}\n")

    last_run = get_last_run_time()
    if last_run:
        print(f"  Last run: {last_run.strftime('%B %d, %Y at %I:%M %p EST')}")
    else:
        print(f"  No previous run found. Using 24-hour lookback for this run.")
    print()

    all_jobs = []

    # --- Step 1: Scrape from 3 platforms ---
    print("[Step 1/6] Scraping jobs from LinkedIn, Indeed, and Dice...\n")

    for title in JOB_TITLES:
        try:
            jobs = scrape_linkedin(title)
            all_jobs.extend(jobs)
        except Exception as e:
            print(f"  [LinkedIn] Error for '{title}': {e}")

        try:
            jobs = scrape_indeed(title)
            all_jobs.extend(jobs)
        except Exception as e:
            print(f"  [Indeed] Error for '{title}': {e}")

        try:
            jobs = scrape_dice(title)
            all_jobs.extend(jobs)
        except Exception as e:
            print(f"  [Dice] Error for '{title}': {e}")

    print(f"\n  Total raw jobs scraped: {len(all_jobs)}\n")

    if not all_jobs:
        print("  No jobs found. Exiting.")
        return

    # --- Step 2: Filter to US only ---
    print("[Step 2/6] Filtering to US-only jobs...\n")
    us_jobs = filter_us_only(all_jobs)

    # --- Step 3: Filter to data-related roles ---
    print("\n[Step 3/6] Filtering to data-related roles...\n")
    data_jobs = filter_data_roles(us_jobs)

    # --- Step 4: Filter by last run timestamp ---
    print("\n[Step 4/6] Filtering to jobs posted since last run...\n")
    recent_jobs = filter_by_last_run(data_jobs, last_run)

    # --- Step 5: Deduplicate (7-day rolling window) ---
    print("\n[Step 5/6] Removing duplicates (7-day rolling dedup)...\n")
    unique_jobs = deduplicate_jobs(recent_jobs)

    if not unique_jobs:
        print("  No new jobs after filtering. Exiting.")
        save_current_run_timestamp()
        return

    # --- Step 6: Score and rank ---
    print("\n[Step 6/6] Scoring and ranking by skill match...\n")
    scored_jobs = filter_and_score_jobs(unique_jobs)

    if not scored_jobs:
        print("  No jobs after scoring. Exiting.")
        save_current_run_timestamp()
        return

    print(f"\n  Final job count: {len(scored_jobs)}")
    print(f"  Jobs with visa sponsorship: {sum(1 for j in scored_jobs if 'yes' in j.get('visa_sponsorship', '').lower())}")

    # --- Generate Excel ---
    print("\n  Generating Excel file...\n")
    filepath = generate_excel(scored_jobs)

    # --- Send email ---
    print("\n  Sending email...\n")
    send_email(filepath, len(scored_jobs))

    # --- Save timestamp for next run ---
    save_current_run_timestamp()

    elapsed = (datetime.now(EST) - start).total_seconds()
    print(f"\n{'='*60}")
    print(f"  PIPELINE COMPLETE")
    print(f"  Jobs found: {len(scored_jobs)}")
    print(f"  Time elapsed: {elapsed:.0f} seconds")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    run_pipeline()
