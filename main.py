"""
Job Hunt Automation Pipeline — Main Orchestrator

This script:
1. Scrapes jobs from LinkedIn, Indeed, Dice, Built In, and Jobright
2. Deduplicates across platforms and previous runs
3. Scores and ranks jobs by skill match
4. Detects visa sponsorship likelihood
5. Generates a formatted Excel file
6. Emails it to you

Designed to run every 4 hours via GitHub Actions.
"""
import sys
from datetime import datetime
from config import JOB_TITLES
from scrapers import scrape_linkedin, scrape_indeed, scrape_dice, scrape_builtin, scrape_jobright
from processing import filter_and_score_jobs, deduplicate_jobs
from output import generate_excel
from notify import send_email


def run_pipeline():
    """Execute the full job scraping pipeline."""
    start = datetime.now()
    print(f"\n{'='*60}")
    print(f"  JOB HUNT AUTOMATION PIPELINE")
    print(f"  Started: {start.strftime('%B %d, %Y at %I:%M %p ET')}")
    print(f"{'='*60}\n")

    all_jobs = []

    # --- Step 1: Scrape from all platforms ---
    print("[Step 1/5] Scraping jobs from all platforms...\n")

    for title in JOB_TITLES:
        # LinkedIn
        try:
            jobs = scrape_linkedin(title)
            all_jobs.extend(jobs)
        except Exception as e:
            print(f"  [LinkedIn] Error for '{title}': {e}")

        # Indeed
        try:
            jobs = scrape_indeed(title)
            all_jobs.extend(jobs)
        except Exception as e:
            print(f"  [Indeed] Error for '{title}': {e}")

        # Dice
        try:
            jobs = scrape_dice(title)
            all_jobs.extend(jobs)
        except Exception as e:
            print(f"  [Dice] Error for '{title}': {e}")

        # Built In
        try:
            jobs = scrape_builtin(title)
            all_jobs.extend(jobs)
        except Exception as e:
            print(f"  [BuiltIn] Error for '{title}': {e}")

    # Jobright (not filtered by title — it has its own curation)
    try:
        jobs = scrape_jobright()
        all_jobs.extend(jobs)
    except Exception as e:
        print(f"  [Jobright] Error: {e}")

    print(f"\n  Total raw jobs scraped: {len(all_jobs)}\n")

    if not all_jobs:
        print("  No jobs found. Exiting.")
        return

    # --- Step 2: Deduplicate ---
    print("[Step 2/5] Removing duplicates...\n")
    unique_jobs = deduplicate_jobs(all_jobs)

    if not unique_jobs:
        print("  No new jobs after deduplication. Exiting.")
        return

    # --- Step 3: Score and rank ---
    print("\n[Step 3/5] Scoring and ranking by skill match...\n")
    scored_jobs = filter_and_score_jobs(unique_jobs)

    if not scored_jobs:
        print("  No jobs after scoring. Exiting.")
        return

    print(f"  Final job count: {len(scored_jobs)}")
    print(f"  Top match score: {scored_jobs[0]['match_score'] if scored_jobs else 'N/A'}")
    print(f"  Jobs with visa sponsorship: {sum(1 for j in scored_jobs if 'yes' in j.get('visa_sponsorship', '').lower())}")

    # --- Step 4: Generate Excel ---
    print("\n[Step 4/5] Generating Excel file...\n")
    filepath = generate_excel(scored_jobs)

    # --- Step 5: Email ---
    print("\n[Step 5/5] Sending email...\n")
    send_email(filepath, len(scored_jobs))

    # Done
    elapsed = (datetime.now() - start).total_seconds()
    print(f"\n{'='*60}")
    print(f"  PIPELINE COMPLETE")
    print(f"  Jobs found: {len(scored_jobs)}")
    print(f"  Time elapsed: {elapsed:.0f} seconds")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    run_pipeline()
