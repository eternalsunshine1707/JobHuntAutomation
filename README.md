# <ins>JOB HUNT AUTOMATION</ins>

I built this because I got tired of checking five different job boards every few hours. As someone on F-1 OPT actively looking for Data Engineer and Data Analyst roles, I needed a way to catch new postings early, you know,  before hundreds of other applicants pile on.

This pipeline scrapes LinkedIn, Indeed, Dice, Built In, and Jobright every few hours, filters out jobs that won't sponsor visas, scores each one against my resume skills, and emails me a clean Excel sheet. I wake up, open my inbox, and start applying to the best matches. No more tab-hopping across job boards.

## Mmm.. What it actually does!?

Every run follows five steps:

1. Scrapes jobs from all five platforms using Apify actors
2. Removes duplicates - both cross-platform (same job on LinkedIn and Indeed) and across runs (jobs I already saw this week)
3. Scores each job as "Great Match," "Good Match," or "Fair Match" based on how well the required skills align with my background (Python, SQL, AWS, Spark, Databricks, ETL, etc.)
4. Filters out any job that explicitly says "no visa sponsorship"
5. Generates a formatted Excel file and emails it to me

The whole thing runs on GitHub Actions - no servers to manage, no infrastructure to maintain. Just a cron schedule and a Python script.

## How it's scheduled?

Weekdays (Mon-Fri): 5:00 AM, 10:00 AM, 2:00 PM, 7:00 PM EST
Weekends (Sat-Sun): 9:00 AM, 5:00 PM EST

The 5 AM run is the most valuable - I get overnight postings before most people even check their email. The timing is based on when US companies typically post jobs (heaviest between 8-11 AM ET, with a second wave in the afternoon from west coast companies).

## Project structure

```
job-hunt-automation/
├── scrapers/
│   ├── linkedin_scraper.py     # curious_coder/linkedin-jobs-scraper
│   ├── indeed_scraper.py       # valig/indeed-jobs-scraper
│   ├── dice_scraper.py         # shahidirfan/Dice-Job-Scraper
│   ├── builtin_scraper.py      # easyapi/builtin-jobs-scraper
│   └── jobright_scraper.py     # Scrapes Jobright's public GitHub H1B repo
├── processing/
│   ├── matcher.py              # Skill scoring and visa sponsorship detection
│   └── deduplicator.py         # 7-day rolling dedup with timestamps
├── output/
│   └── excel_generator.py      # Formatted xlsx with hyperlinks and color coding
├── notify/
│   └── emailer.py              # Gmail SMTP with attachment
├── main.py                     # Orchestrates everything
├── config.py                   # All settings in one place
└── .github/workflows/
    └── job_search.yml          # GitHub Actions cron schedule
```

## The Excel output

Each sheet includes: job number, company, title, location, source platform, posting time, applicant count (when available), match score, visa sponsorship status, and a clickable apply link. Visa status is color-coded: Green for "Yes," Yellow for "Unknown." Jobs that explicitly say "No" to sponsorship are removed before the sheet is generated.

The filename includes the date and time in EST so I can easily track which run produced which results.

## Tech stack

- Python 3.11
- Apify (scraping actors for each platform)
- openpyxl (Excel generation)
- Gmail SMTP (email delivery via App Password)
- GitHub Actions (scheduled automation)

## Setup

If you want to use this yourself, you'll need:

1. An Apify account with an API token (Starter plan at $29/month covers it comfortably)
2. A Gmail account with an App Password enabled (not your regular password - Google requires a 16-character app-specific password for SMTP)
3. A GitHub repo with four secrets configured: `APIFY_API_TOKEN`, `EMAIL_SENDER`, `EMAIL_APP_PASSWORD`, `EMAIL_RECIPIENT`

Clone the repo, push to GitHub, and trigger the first run manually from the Actions tab. After that, the schedule handles everything automatically.

Edit `config.py` to change job titles, target skills, or the list of known H1B sponsors. The skills list is what drives the match scoring - update it to reflect your own resume.

## Cost

GitHub Actions is free for public repos. Apify's Starter plan gives $29/month in credits. With 24 runs per week across 5 platforms, I'm spending roughly $12-15/month - well within the budget. The cost per job listing is between $0.001 and $0.005 depending on the platform.

## What I'd do differently next time!?

If I were starting over, I'd probably skip the RAG web browser approach for Built In entirely and go straight for the dedicated scraper. I spent more time debugging field name mismatches than I'd like to admit. Testing each scraper's actual API output before writing the parsing code would have saved hours.

I'm also considering migrating the scheduler from GitHub Actions to AWS Lambda with EventBridge at some point - partly because it's a better fit architecturally, and partly because it'd be a good thing to talk about in interviews given my AWS background.

## License

MIT - Use it however you want!

---

Built by Sravani Brahamma Routhu | [LinkedIn](https://www.linkedin.com/in/sravaniofficial/)
