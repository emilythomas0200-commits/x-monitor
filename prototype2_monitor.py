import os
import smtplib
import feedparser
from email.message import EmailMessage
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

EMAIL = os.environ["EMAIL_ADDRESS"]
APP_PASSWORD = os.environ["EMAIL_PASSWORD"]
STATE_FILE = "last_tweet.txt"

NITTER_INSTANCES = [
    "https://nitter.net",
    "https://nitter.privacydev.net",
    "https://nitter.poast.org",
]
USERNAME = "iamjakestream"

def get_latest_tweet():
    for instance in NITTER_INSTANCES:
        try:
            feed = feedparser.parse(f"{instance}/{USERNAME}/rss")
            if not feed.entries:
                continue
            entries = sorted(feed.entries, key=lambda e: parsedate_to_datetime(e.get("published", "Thu, 01 Jan 1970 00:00:00 GMT")), reverse=True)
            cutoff = datetime.now(timezone.utc) - timedelta(days=7)
            entries = [e for e in entries if parsedate_to_datetime(e.get("published", "Thu, 01 Jan 1970 00:00:00 GMT")) > cutoff]
            # Filter out retweets, keep original posts, replies and quote tweets
            entries = [e for e in entries if not e.get("title", "").startswith("RT by")]
            if entries:
                latest = entries[0]
                return {
                    "id": latest.get("id", latest.get("link", "")),
                    "text": latest.get("title", ""),
                    "link": latest.get("link", "").replace("nitter.net", "x.com").replace("#m", ""),
                    "published": latest.get("published", "")
                }
        except Exception as e:
            print(f"Error with {instance}: {e}")
    return None

def send_email(tweet):
    msg = EmailMessage()
    msg.set_content(
        f"X Monitoring Alert!\n\n"
        f"@{USERNAME} just posted:\n\n"
        f"{tweet['text']}\n\n"
        f"Link: {tweet['link']}\n"
        f"Posted: {tweet['published']}\n\n"
        f"This is an automated OSINT monitoring alert."
    )
    msg["Subject"] = f"X Monitoring Alert - @{USERNAME} posted"
    msg["From"] = EMAIL
    msg["To"] = EMAIL
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL, APP_PASSWORD)
        smtp.send_message(msg)

def load_last():
    try:
        with open(STATE_FILE, "r") as f:
            return f.read().strip()
    except:
        return None

def save_last(val):
    with open(STATE_FILE, "w") as f:
        f.write(str(val))

print("X Monitor Running...")
latest = get_latest_tweet()
print(f"Latest tweet: {latest}")
previous = load_last()
print(f"Previous tweet ID: {previous}")

if latest:
    if previous != latest["id"]:
        print("New tweet detected!")
        send_email(latest)
        save_last(latest["id"])
    else:
        print("No new tweets.")
else:
    print("No tweets found.")
