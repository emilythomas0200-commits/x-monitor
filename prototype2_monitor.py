import os
import smtplib
import time
from email.message import EmailMessage
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

EMAIL = os.environ["EMAIL_ADDRESS"]
APP_PASSWORD = os.environ["EMAIL_PASSWORD"]
STATE_FILE = "last_tweet.txt"

def get_latest_tweet():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://x.com/iamjakestream")
    time.sleep(8)
    
    try:
        articles = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
        for article in articles:
            if "Pinned" in article.text:
                continue
            tweets = article.find_elements(By.XPATH, './/div[@data-testid="tweetText"]')
            if tweets:
                result = tweets[0].text
                driver.quit()
                return result
    except Exception as e:
        print(f"Error: {e}")
    
    driver.quit()
    return None

def send_email(tweet):
    msg = EmailMessage()
    msg.set_content(
        f"🚨 X Monitoring Alert!\n\n"
        f"@iamjakestream just posted:\n\n"
        f"{tweet}\n\n"
        f"This is an automated OSINT monitoring alert."
    )
    msg["Subject"] = "🚨 X Monitoring Alert - @iamjakestream posted"
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
print(f"Previous tweet: {previous}")

if latest:
    if previous != latest:
        print("🚨 New tweet detected!")
        send_email(latest)
        save_last(latest)
    else:
        print("No new tweets.")
else:
    print("No tweets found.")
