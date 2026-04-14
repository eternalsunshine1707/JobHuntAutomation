"""
Deduplicator - Tracks seen jobs across runs to avoid sending duplicates.
Uses a JSON file to persist job IDs between runs.
"""
import json
import hashlib
import os
from config import SEEN_JOBS_FILE


def generate_job_id(job: dict) -> str:
    """Generate a unique ID for a job based on company + title + location."""
    raw = f"{job.get('company', '')}|{job.get('title', '')}|{job.get('location', '')}".lower().strip()
    return hashlib.md5(raw.encode()).hexdigest()


def load_seen_jobs() -> set:
    """Load previously seen job IDs from file."""
    if os.path.exists(SEEN_JOBS_FILE):
        try:
            with open(SEEN_JOBS_FILE, "r") as f:
                data = json.load(f)
                return set(data.get("seen_ids", []))
        except (json.JSONDecodeError, KeyError):
            return set()
    return set()


def save_seen_jobs(seen_ids: set):
    """Save seen job IDs to file."""
    # Keep only last 5000 IDs to prevent file from growing forever
    ids_list = list(seen_ids)[-5000:]
    with open(SEEN_JOBS_FILE, "w") as f:
        json.dump({"seen_ids": ids_list}, f)


def deduplicate_jobs(jobs: list[dict]) -> list[dict]:
    """Remove jobs that have been seen in previous runs AND remove cross-platform duplicates."""
    seen_ids = load_seen_jobs()
    new_jobs = []
    current_run_ids = set()

    for job in jobs:
        job_id = generate_job_id(job)

        # Skip if seen in previous runs or already in this batch
        if job_id in seen_ids or job_id in current_run_ids:
            continue

        current_run_ids.add(job_id)
        job["job_id"] = job_id
        new_jobs.append(job)

    # Save all IDs (old + new)
    all_ids = seen_ids | current_run_ids
    save_seen_jobs(all_ids)

    print(f"  [Dedup] {len(jobs)} total → {len(new_jobs)} new (filtered {len(jobs) - len(new_jobs)} duplicates)")
    return new_jobs
