"""
Configuration for Job Hunt Automation Pipeline.
All settings in one place - edit this file to customize your job search.
"""
import os

# --- Apify API ---
APIFY_API_TOKEN = os.environ.get("APIFY_API_TOKEN", "")

# --- Email ---
EMAIL_SENDER = os.environ.get("EMAIL_SENDER", "")
EMAIL_PASSWORD = os.environ.get("EMAIL_APP_PASSWORD", "")  # Gmail App Password
EMAIL_RECIPIENT = os.environ.get("EMAIL_RECIPIENT", "sravanistar99@gmail.com")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# --- Job Search Parameters ---
JOB_TITLES = ["Data Engineer", "Data Analyst"]
LOCATIONS = ["United States"]
MAX_JOBS_PER_PLATFORM = 100
DATE_POSTED_FILTER = "1"  # 1 = last 24 hours (closest filter available on most platforms)

# --- Platforms ---
PLATFORMS = ["linkedin", "indeed", "dice", "builtin"]

# --- Skills for matching/scoring (from resume) ---
CORE_SKILLS = [
    "python", "sql", "pyspark", "aws", "databricks", "snowflake",
    "spark", "airflow", "etl", "elt", "glue", "lambda", "s3",
    "redshift", "delta lake", "kafka", "terraform", "dbt",
    "great expectations", "tableau", "power bi", "pandas",
    "postgresql", "mysql", "mongodb", "dynamodb", "docker",
    "jenkins", "git", "ci/cd", "react", "javascript",
    "r", "excel", "data pipeline", "data warehouse",
    "data lake", "medallion", "bronze", "silver", "gold"
]

# --- Visa Sponsorship Keywords ---
VISA_POSITIVE = [
    "visa sponsorship", "h1b", "h-1b", "sponsor", "opt",
    "f-1", "f1", "stem opt", "immigration sponsorship",
    "sponsorship available", "will sponsor", "open to sponsorship"
]
VISA_NEGATIVE = [
    "no sponsorship", "not sponsor", "unable to sponsor",
    "without sponsorship", "cannot sponsor", "won't sponsor",
    "not eligible for sponsorship", "no visa", "citizen only",
    "permanent resident only", "authorized to work without"
]

# --- Deduplication ---
SEEN_JOBS_FILE = "seen_jobs.json"

# --- Output ---
OUTPUT_DIR = "output_files"
