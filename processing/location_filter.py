"""
Location Filter - Only keeps jobs located in the United States.
Rejects jobs in India, Canada, UK, Europe, etc. even if the platform's
country filter let them through.
"""

# US state abbreviations and full names
US_STATES = {
    "al", "ak", "az", "ar", "ca", "co", "ct", "de", "fl", "ga", "hi", "id",
    "il", "in", "ia", "ks", "ky", "la", "me", "md", "ma", "mi", "mn", "ms",
    "mo", "mt", "ne", "nv", "nh", "nj", "nm", "ny", "nc", "nd", "oh", "ok",
    "or", "pa", "ri", "sc", "sd", "tn", "tx", "ut", "vt", "va", "wa", "wv",
    "wi", "wy", "dc",
    "alabama", "alaska", "arizona", "arkansas", "california", "colorado",
    "connecticut", "delaware", "florida", "georgia", "hawaii", "idaho",
    "illinois", "indiana", "iowa", "kansas", "kentucky", "louisiana",
    "maine", "maryland", "massachusetts", "michigan", "minnesota",
    "mississippi", "missouri", "montana", "nebraska", "nevada",
    "new hampshire", "new jersey", "new mexico", "new york", "north carolina",
    "north dakota", "ohio", "oklahoma", "oregon", "pennsylvania",
    "rhode island", "south carolina", "south dakota", "tennessee", "texas",
    "utah", "vermont", "virginia", "washington", "west virginia",
    "wisconsin", "wyoming",
}

US_INDICATORS = {
    "united states", "usa", "u.s.", "u.s.a", "us ", " us", "-us", "us-",
    "remote us", "remote - us", "remote (us)", "us remote",
}

# Countries that are definitely NOT US — hard reject
NON_US_COUNTRIES = {
    "india", "canada", "mexico", "united kingdom", "uk ", " uk", "-uk",
    "england", "scotland", "wales", "ireland", "germany", "france",
    "spain", "italy", "netherlands", "poland", "romania", "ukraine",
    "australia", "new zealand", "singapore", "philippines", "malaysia",
    "japan", "china", "south korea", "hong kong", "taiwan", "vietnam",
    "brazil", "argentina", "chile", "colombia", "peru", "south africa",
    "nigeria", "egypt", "kenya", "israel", "turkey", "greece", "portugal",
    "sweden", "norway", "denmark", "finland", "switzerland", "austria",
    "belgium", "czech", "hungary", "bulgaria", "serbia", "croatia",
    "dubai", "saudi arabia", "qatar", "oman", "pakistan", "bangladesh",
}


def is_us_location(location: str) -> bool:
    """Determine if a location string refers to the United States."""
    if not location:
        return False

    loc = location.lower().strip()

    # Hard reject if a non-US country is mentioned
    for country in NON_US_COUNTRIES:
        if country in loc:
            return False

    # Accept if explicit US indicator
    for indicator in US_INDICATORS:
        if indicator in loc:
            return True

    # Accept if a US state is mentioned
    # Split on common separators and check each part
    parts = []
    for sep in [",", "/", "|", "-", "·", "•"]:
        loc = loc.replace(sep, " ")
    parts = loc.split()

    for part in parts:
        if part.strip(".,;:()[]").strip() in US_STATES:
            return True

    # "Remote" alone without US indicator - assume US if no other country given
    if loc.strip() in ("remote", "remote work", "anywhere", "nationwide"):
        return True

    return False


def filter_us_only(jobs: list[dict]) -> list[dict]:
    """Remove any jobs that are clearly not in the United States."""
    kept = []
    rejected = 0

    for job in jobs:
        loc = job.get("location", "")
        if is_us_location(loc):
            kept.append(job)
        else:
            rejected += 1

    print(f"  [LocationFilter] {len(jobs)} → {len(kept)} (rejected {rejected} non-US)")
    return kept
