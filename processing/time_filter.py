"""
Time Filter - Only keeps jobs posted since the last successful run.
Uses Approach B with fallback: unparseable timestamps are kept.
"""
import json
import os
import re
from datetime import datetime, timezone, timedelta
from config import LAST_RUN_FILE

UTC = timezone.utc
EST = timezone(timedelta(hours=-4))


def get_last_run_time():
    """Read last run timestamp from file. Returns None if not found."""
    if not os.path.exists(LAST_RUN_FILE):
        return None
    try:
        with open(LAST_RUN_FILE, "r") as f:
            data = json.load(f)
            ts = data.get("last_run_utc")
            if ts:
                return datetime.fromisoformat(ts).astimezone(EST)
    except Exception:
        pass
    return None


def save_current_run_timestamp():
    """Save current run timestamp for next run to use."""
    now = datetime.now(UTC).isoformat()
    try:
        with open(LAST_RUN_FILE, "w") as f:
            json.dump({"last_run_utc": now}, f)
        print(f"  [TimeFilter] Saved current run timestamp: {now}")
    except Exception as e:
        print(f"  [TimeFilter] Could not save timestamp: {e}")


def parse_posted_time(posted_str: str, now: datetime):
    """
    Parse a job's posted_time string into a datetime.
    Returns None if unparseable (caller decides what to do).

    Handles:
    - ISO timestamps: 2026-04-14T22:13:15.678Z
    - Relative: "Reposted 15 days ago", "2 hours ago", "Yesterday"
    - Vague: "Today", "Recently posted", "Recent" → None (fallback keeps them)
    """
    if not posted_str or posted_str == "Unknown":
        return None

    s = str(posted_str).strip().lower()

    # Try ISO format first (Indeed, LinkedIn often use this)
    try:
        clean = posted_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt
    except Exception:
        pass

    # "X hours ago", "X minutes ago"
    m = re.search(r"(\d+)\s*(minute|hour|day|week)s?\s*ago", s)
    if m:
        num = int(m.group(1))
        unit = m.group(2)
        if unit == "minute":
            return now - timedelta(minutes=num)
        elif unit == "hour":
            return now - timedelta(hours=num)
        elif unit == "day":
            return now - timedelta(days=num)
        elif unit == "week":
            return now - timedelta(weeks=num)

    # "Reposted X days ago"
    m = re.search(r"reposted\s+(\d+)\s*(hour|day|week)s?\s*ago", s)
    if m:
        num = int(m.group(1))
        unit = m.group(2)
        if unit == "hour":
            return now - timedelta(hours=num)
        elif unit == "day":
            return now - timedelta(days=num)
        elif unit == "week":
            return now - timedelta(weeks=num)

    # "Yesterday"
    if "yesterday" in s:
        return now - timedelta(days=1)

    # Vague terms — return None so caller keeps the job
    if any(vague in s for vague in ["today", "recent", "just posted", "new"]):
        return None

    # Unparseable — keep the job (fallback)
    return None


def filter_by_last_run(jobs: list[dict], last_run) -> list[dict]:
    """
    Keep only jobs posted after the last run timestamp.
    If last_run is None, use a 24-hour lookback as fallback.
    Jobs with unparseable timestamps are kept (to avoid missing good ones).
    """
    now = datetime.now(UTC)
    cutoff = last_run.astimezone(UTC) if last_run else (now - timedelta(hours=24))

    kept = []
    rejected_too_old = 0
    kept_unparseable = 0

    for job in jobs:
        posted_dt = parse_posted_time(job.get("posted_time", ""), now)

        if posted_dt is None:
            # Unparseable — keep it (dedup will handle repeats)
            kept.append(job)
            kept_unparseable += 1
            continue

        if posted_dt < cutoff:
            rejected_too_old += 1
            continue

        kept.append(job)

    print(f"  [TimeFilter] {len(jobs)} → {len(kept)} (rejected {rejected_too_old} old, kept {kept_unparseable} unparseable)")
    return kept
