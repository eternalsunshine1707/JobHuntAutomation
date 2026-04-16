# Job Hunt Automation

I built this because I got tired of refreshing LinkedIn, Indeed, and Dice every few hours to see what was new. As someone on F-1 OPT actively looking for Data Engineer and Data Analyst roles, being one of the first 50 applicants makes a real difference. This tool handles the checking for me and sends me a clean Excel sheet with the relevant jobs so I can focus on actually applying.

## What it does

The pipeline runs on a schedule (more on that below), scrapes new postings from three platforms, filters out the noise, and emails me the results as a formatted Excel file.

Specifically, each run:

1. Scrapes fresh listings from LinkedIn, Indeed, and Dice using Apify actors
2. Keeps only jobs located in the United States (filters out results from India, Canada, UK, and elsewhere)
3. Keeps only data-related roles (Data Engineer, Data Analyst, Analytics Engineer, BI Developer, etc. — including junior and entry-level positions)
4. Filters out anything posted before the last run — I only want to see jobs that are genuinely new since I last checked
5. Removes duplicates using a 7-day rolling window (so I don't see the same job from LinkedIn and Indeed twice, and don't see repeats across runs)
6. Scores each remaining job as "Great Match," "Good Match," or "Fair Match" based on how well the skill requirements align with my resume
7. Flags visa sponsorship status and removes jobs that explicitly say no
8. Generates an Excel file with clickable apply links and emails it to me

## Schedule

The thing that surprised me most about this project is how much the timing matters. Applying within the first two hours of a posting dramatically improves your callback rate. So the schedule is built around catching jobs early:

- **Weekdays (Mon–Fri):** 4:00 AM, 11:00 AM, 6:00 PM EST
- **Weekends (Sat–Sun):** 10:00 AM EST

The 4 AM run is the most valuable one. It catches everything posted overnight — by the time everyone else is checking their email at 9 AM, I've already applied. The 11 AM run catches the heavy morning posting window (8-11 AM ET is when most companies post), and the 6 PM run picks up late-day postings from west coast companies.

GitHub Actions cron can be delayed by 5-30 minutes sometimes, which is why the times are slightly earlier than you might expect. A 4 AM run arriving at 4:30 is still early enough to matter.

## Project structure

```
job-hunt-automation/
├── scrapers/
│   ├── linkedin_scraper.py     # curious_coder/linkedin-jobs-scraper
│   ├── indeed_scraper.py       # valig/indeed-jobs-scraper
│   └── dice_scraper.py         # shahidirfan/Dice-Job-Scraper
├── processing/
│   ├── matcher.py              # Skill scoring and visa detection
│   ├── deduplicator.py         # 7-day rolling dedup with timestamps
│   ├── time_filter.py          # Filters to jobs posted since last run
│   ├── location_filter.py      # Rejects non-US jobs
│   └── role_filter.py          # Keeps only data-related roles
├── output/
│   └── excel_generator.py      # Formatted xlsx with hyperlinks
├── notify/
│   └── emailer.py              # Gmail SMTP with attachment
├── main.py                     # Orchestrates the full pipeline
├── config.py                   # All settings in one place
└── .github/workflows/
    └── job_search.yml          # Cron schedule
```

## The Excel output

Each email contains a single Excel sheet with the run's findings. Columns include company, job title, location, source platform, posted time, applicant count (when the platform provides it), match score, visa sponsorship status, and a clickable apply link. Visa status is color-coded — green for confirmed sponsorship, yellow for unknown. Jobs that explicitly don't sponsor are filtered out before the sheet is generated.

The filename and sheet title include the date and time in EST, so I can easily look back at past runs to track what I applied to and when.

## Tech stack

Python 3.11. Apify actors for scraping (paid, but the Starter plan covers my usage comfortably). openpyxl for the Excel generation. Gmail SMTP for sending. GitHub Actions for the scheduling — it's free for public repos and handles everything server-side.

## Setup

To use this yourself you'll need:

- An Apify account and API token
- A Gmail account with an App Password enabled (Google requires the 16-character app-specific password for SMTP access)
- A GitHub repo with four secrets configured: `APIFY_API_TOKEN`, `EMAIL_SENDER`, `EMAIL_APP_PASSWORD`, `EMAIL_RECIPIENT`

Clone the repo, push to your own GitHub, and trigger the first run manually from the Actions tab. After that the schedule runs automatically. The `last_run.json` file is cached between runs so the pipeline always knows where it left off.

Edit `config.py` to change job titles, skills, or the list of known sponsors. The skills list drives the match scoring — update it to reflect your own background if you fork this.

## Cost

GitHub Actions is free. Apify's Starter plan is $29/month with $29 in usage credits included. With the current schedule (17 runs per week across 3 platforms), I'm spending around $20-25/month, comfortably within budget.

I did experiment with Built In and Jobright scrapers early on but dropped them. Built In was the most expensive scraper by far (nearly 3x the cost per result) and Jobright's data quality was inconsistent. LinkedIn, Indeed, and Dice cover the vast majority of listings I care about anyway.

## Things I'd do differently next time

Test each scraper's actual API output before writing the parsing code. I spent way more time than I should have debugging field name mismatches — what I thought was `jobUrl` turned out to be `link`, what I thought was `company` turned out to be `employer.name`, and so on. Running the actor once, inspecting the output, and then writing the scraper would have saved hours.

The other thing I underestimated was how each platform implements its "last 24 hours" filter. Most of them include reposted listings in that window, which meant I was getting jobs from 2-3 weeks ago showing up as new. The fix was to add my own time filter that reads the posting timestamp from each job and compares it against the last run's end time — ignoring what the platform claims the date filter does.

## What's next

A few things I'd like to add when I have time:

- Migrating from GitHub Actions to AWS Lambda with EventBridge. GitHub's cron delays can be a few minutes to half an hour, which isn't ideal when timing matters. Lambda would also make for a cleaner portfolio talking point given my AWS background.
- Auto-generating tailored cover letters using Claude for the top matches
- A simple dashboard to track application status (applied, phone screen, on-site, rejected)
- Monitoring the career pages of specific dream companies directly, separately from the general scrape

## License

MIT. Use it, fork it, adapt it to your own job search.

---

Built by Sravani Brahamma Routhu | [LinkedIn](https://www.linkedin.com/in/sravaniofficial/)
