# src/scraper.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

import pandas as pd
import time
import re
import os
import random
from datetime import datetime, timedelta

BASE_URL = "https://www.drikpanchang.com/panchang/day-panchang.html?date={date}&geoname-id=1277333"


def make_driver():
    options = webdriver.ChromeOptions()
    #options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )


def scrape_day(driver, date_obj) -> dict | None:
    formatted = date_obj.strftime("%d/%m/%Y")
    url = BASE_URL.format(date=formatted)

    try:
        driver.get(url)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(2)

        body = driver.find_element(By.TAG_NAME, "body").text

        sunrise_match = re.search(r"Sunrise\s*([0-9]{1,2}:[0-9]{2}\s*[APap][Mm])", body)
        sunset_match  = re.search(r"Sunset\s*([0-9]{1,2}:[0-9]{2}\s*[APap][Mm])", body)

        if sunrise_match and sunset_match:
            return {
                "date":    date_obj.strftime("%Y-%m-%d"),
                "city":    "Bengaluru",
                "sunrise": sunrise_match.group(1).strip(),
                "sunset":  sunset_match.group(1).strip(),
            }
        else:
            # Print exactly what the page shows around Sunrise
            idx = body.lower().find("sunrise")
            if idx >= 0:
                print(f"  [MISS] {formatted} — found 'Sunrise' but regex failed")
                print(f"         Context: '{body[idx:idx+60]}'")
            else:
                print(f"  [MISS] {formatted} — 'Sunrise' not in page at all")
                print(f"         Page length: {len(body)} chars")
                print(f"         First 100 chars: {body[:100]}")
            return None

    except Exception as e:
        print(f"  [ERROR] {formatted}: {e}")
        return None


def scrape_year(year: int):

    print(f"Scraping Bengaluru for {year}...")

    BATCH_SIZE = 30

    driver = make_driver()

    count = 0

    records = []

    start = datetime(year, 1, 1)
    end = datetime(year, 12, 31)

    current = start

    try:

        while current <= end:

            # restart browser every 30 requests
            if count > 0 and count % BATCH_SIZE == 0:

                print("\nRestarting browser session...\n")

                driver.quit()

                time.sleep(random.uniform(5, 8))

                driver = make_driver()

            record = scrape_day(driver, current)

            if record:
                records.append(record)

            # auto-save every 20 records
            if len(records) % 20 == 0 and len(records) > 0:

                temp_df = pd.DataFrame(records)

                os.makedirs("data/raw", exist_ok=True)

                temp_df.to_csv(
                    f"data/raw/daylight_raw_{year}.csv",
                    index=False
                )

                print(f"Checkpoint saved ({len(records)} records)")

            time.sleep(random.uniform(2, 5))

            current += timedelta(days=1)

            count += 1

    finally:

        driver.quit()

    df = pd.DataFrame(records)

    os.makedirs("data/raw", exist_ok=True)

    out = f"data/raw/daylight_raw_{year}.csv"

    df.to_csv(out, index=False)

    print(f"\n✅ Done — {len(df)}/365 days saved → {out}")

    return df


if __name__ == "__main__":
    import sys
    year = int(sys.argv[1]) if len(sys.argv) > 1 else 2025
    scrape_year(year)