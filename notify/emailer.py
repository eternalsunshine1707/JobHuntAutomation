"""
Email Notifier - Sends the Excel file to Gmail using SMTP.
Requires a Gmail App Password (not your regular Gmail password).
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from datetime import datetime, timezone, timedelta
from config import EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECIPIENT, SMTP_SERVER, SMTP_PORT

EST = timezone(timedelta(hours=-4))


def send_email(filepath: str, job_count: int):
    """Send the Excel file as an email attachment."""
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        print("  [Email] Skipped — EMAIL_SENDER or EMAIL_APP_PASSWORD not set")
        return

    now_est = datetime.now(EST)
    date_str = now_est.strftime("%b %d, %Y")
    time_str = now_est.strftime("%I:%M %p EST")

    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECIPIENT
    msg["Subject"] = f"Job Search Results | {date_str} | {time_str}"

    body = f"""Hi Sravani,

Your automated job search found {job_count} new listings across LinkedIn, Indeed, Dice, Built In, and Jobright.

The attached Excel file contains all jobs sorted by skill match, with visa sponsorship status flagged.

— Job Hunt Automation Bot
"""
    msg.attach(MIMEText(body, "plain"))

    # Attach Excel file
    try:
        with open(filepath, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
            encoders.encode_base64(part)
            filename = filepath.split("/")[-1]
            part.add_header("Content-Disposition", f"attachment; filename={filename}")
            msg.attach(part)
    except Exception as e:
        print(f"  [Email] Failed to attach file: {e}")
        return

    # Send
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"  [Email] Sent to {EMAIL_RECIPIENT} with {job_count} jobs")
    except Exception as e:
        print(f"  [Email] Failed to send: {e}")
