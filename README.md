# 🔍 Job Hunt Automation Pipeline

An automated job scraping pipeline that searches LinkedIn, Indeed, Dice, Built In, and Jobright every 4 hours, scores jobs by skill match, detects visa sponsorship likelihood, and emails you a formatted Excel report.

Built with Python, Apify, and GitHub Actions.

## 🎯 What It Does

Every 4 hours, this pipeline automatically:

1. **Scrapes** jobs from 5 platforms (LinkedIn, Indeed, Dice, Built In, Jobright)
2. **Deduplicates** across platforms and previous runs — you never see the same job twice
3. **Scores** each job by how well it matches your skills (0-100)
4. **Detects** visa sponsorship status (Yes / No / Unknown)
5. **Generates** a formatted Excel file with hyperlinks, color-coded visa status
6. **Emails** the file to your inbox

## 🏗️ Architecture

```
GitHub Actions (cron: every 4 hrs)
        │
        ▼
    main.py (orchestrator)
        │
        ├── scrapers/          → Calls Apify actors for each platform
        ├── processing/        → Dedup + skill matching + visa detection
        ├── output/            → Excel generation with formatting
        └── notify/            → Gmail SMTP email with attachment
```

## 📁 Project Structure

```
job-hunt-automation/
├── .github/workflows/
│   └── job_search.yml          # GitHub Actions workflow
├── scrapers/
│   ├── linkedin_scraper.py     # LinkedIn via Apify
│   ├── indeed_scraper.py       # Indeed via Apify
│   ├── dice_scraper.py         # Dice via Apify
│   ├── builtin_scraper.py      # Built In via Apify RAG browser
│   └── jobright_scraper.py     # Jobright H1B jobs via GitHub
├── processing/
│   ├── matcher.py              # Skill scoring + visa detection
│   └── deduplicator.py         # Cross-run deduplication
├── output/
│   └── excel_generator.py      # Formatted .xlsx generator
├── notify/
│   └── emailer.py              # Gmail SMTP sender
├── main.py                     # Pipeline orchestrator
├── config.py                   # All configuration
├── requirements.txt
└── README.md
```

## 🚀 Setup

### Prerequisites
- Python 3.11+
- [Apify account](https://apify.com/) (free tier works)
- Gmail account with App Password enabled

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/job-hunt-automation.git
cd job-hunt-automation
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up Gmail App Password

You need a Gmail App Password (not your regular password):

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable **2-Step Verification** if not already enabled
3. Go to [App Passwords](https://myaccount.google.com/apppasswords)
4. Select "Mail" and "Other (Custom name)" → enter "Job Bot"
5. Copy the 16-character password — this is your `EMAIL_APP_PASSWORD`

### 4. Test locally
```bash
export APIFY_API_TOKEN="your_apify_token"
export EMAIL_SENDER="your_email@gmail.com"
export EMAIL_APP_PASSWORD="your_16_char_app_password"
export EMAIL_RECIPIENT="sravanistar99@gmail.com"

python main.py
```

### 5. Set up GitHub Actions

Add these secrets in your GitHub repo → Settings → Secrets and variables → Actions:

| Secret Name | Value |
|---|---|
| `APIFY_API_TOKEN` | Your Apify API token |
| `EMAIL_SENDER` | Your Gmail address |
| `EMAIL_APP_PASSWORD` | Gmail App Password (16 chars) |
| `EMAIL_RECIPIENT` | sravanistar99@gmail.com |

### 6. Trigger manually

Go to **Actions** tab → **Job Hunt Automation** → **Run workflow** → Click the green button.

After that, it runs automatically every 4 hours.

## ⚙️ Configuration

Edit `config.py` to customize:

- **Job titles**: Add or remove target roles
- **Skills**: Update `CORE_SKILLS` to match your resume
- **Max jobs**: Adjust `MAX_JOBS_PER_PLATFORM`
- **Known sponsors**: Add companies to the visa detection list

## 💰 Cost

- **GitHub Actions**: Free (2,000 mins/month on private repos, unlimited on public)
- **Apify scrapers**: ~$0.001–0.005 per job listing
- **Estimated daily cost**: $0.50–2.00 for 6 runs across 5 platforms

## 🛠️ Tech Stack

- **Python 3.11** — Core language
- **Apify** — Job scraping actors (LinkedIn, Indeed, Dice)
- **openpyxl** — Excel file generation
- **GitHub Actions** — Scheduled automation (cron)
- **Gmail SMTP** — Email delivery

## 📊 Sample Output

The Excel file includes:
- Job # | Company | Title | Location | Source | Posted | Applicants | Visa Sponsorship | Apply Link
- Color-coded visa status (green = Yes, yellow = Unknown, red = No)
- Clickable hyperlinks to apply directly
- Sorted by skill match score

## 🔮 Future Improvements

- [ ] Migrate scheduler to AWS Lambda + EventBridge
- [ ] Add Slack/Discord notifications
- [ ] Build a dashboard to track application status
- [ ] Add salary range extraction
- [ ] Auto-generate tailored cover letters per job

## 📝 License

MIT License — use it, modify it, share it.

## 👤 Author

**Sravani Brahamma Routhu**
- [LinkedIn](https://www.linkedin.com/in/sravaniofficial/)
- [Email](mailto:sravanistar99@gmail.com)
