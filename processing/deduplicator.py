"""
Deduplicator - Tracks seen jobs across runs to avoid sending duplicates.
Keeps a 7-day history. Jobs older than 7 days are cleared automatically.
"""
import json
import hashlib
import os
import time
from config import SEEN_JOBS_FILE

SEVEN_DAYS = 7 * 24 * 60 * 60  # seconds


def generate_job_id(job: dict) -> str:
    """Generate a unique ID for a job based on company + title + location."""
    raw = f"{job.get('company', '')}|{job.get('title', '')}|{job.get('location', '')}".lower().strip()
    return hashlib.md5(raw.encode()).hexdigest()


def load_seen_jobs() -> dict:
    """Load previously seen job IDs with timestamps."""
    if os.path.exists(SEEN_JOBS_FILE):
        try:
            with open(SEEN_JOBS_FILE, "r") as f:
                data = json.load(f)
                # Clean out entries older than 7 days
                now = time.time()
                cleaned = {k: v for k, v in data.items() if now - v < SEVEN_DAYS}
                return cleaned
        except (json.JSONDecodeError, KeyError, TypeError):
            return {}
    return {}


def save_seen_jobs(seen: dict):
    """Save seen job IDs with timestamps."""
    with open(SEEN_JOBS_FILE, "w") as f:
        json.dump(seen, f)


def deduplicate_jobs(jobs: list[dict]) -> list[dict]:
    """Remove jobs seen in previous runs (last 7 days) and cross-platform duplicates."""
    seen = load_seen_jobs()
    new_jobs = []
    current_run_ids = set()
    now = time.time()

    for job in jobs:
        job_id = generate_job_id(job)

        # Skip if seen in previous runs (last 7 days) or already in this batch
        if job_id in seen or job_id in current_run_ids:
            continue

        current_run_ids.add(job_id)
        seen[job_id] = now
        job["job_id"] = job_id
        new_jobs.append(job)

    save_seen_jobs(seen)
    print(f"  [Dedup] {len(jobs)} total → {len(new_jobs)} new (filtered {len(jobs) - len(new_jobs)} duplicates, 7-day history)")
    return new_jobs
