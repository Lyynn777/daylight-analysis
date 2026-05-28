# src/scraper_actions.py
# Optimised for GitHub Actions — Linux Chrome, no display

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

import pandas as pd
import time
import re
import os
import sys
from datetime import datetime, timedelta

CITIES = {
    "Bengaluru": 1277333,
    "Delhi":     1273294,
    "Mumbai":    1275339,
    "Chennai":   1264527,
    "Kolkata":   1275004,
}

BASE_URL = (
    "https://www.drikpanchang.com/panchang/day-panchang.html"
    "?date={date}&geoname-id={geoname}"
)


def make_driver():
    """Chrome driver configured for Linux GitHub Actions environment."""
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=opts
    )


def scrape_day(driver, date_obj, city_name, geoname_id) -> dict | None:
    formatted = date_obj.strftime("%d/%m/%Y")
    url = BASE_URL.format(date=formatted, geoname=geoname_id)

    for attempt in range(3):
        try:
            driver.get(url)
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(3)

            body = driver.find_element(By.TAG_NAME, "body").text

            if len(body.strip()) < 100:
                time.sleep(10)
                continue

            sr = re.search(r"Sunrise\s*([0-9]{1,2}:[0-9]{2}\s*[APap][Mm])", body)
            ss = re.search(r"Sunset\s*([0-9]{1,2}:[0-9]{2}\s*[APap][Mm])",  body)

            if sr and ss:
                return {
                    "date":    date_obj.strftime("%Y-%m-%d"),
                    "city":    city_name,
                    "sunrise": sr.group(1).strip(),
                    "sunset":  ss.group(1).strip(),
                }

            # If blocked, wait longer before retry
            if "captcha" in body.lower() or len(body) < 200:
                print(f"  [BLOCKED] {formatted} — waiting 30s")
                time.sleep(30)

        except Exception as e:
            print(f"  [ERROR] {formatted} attempt {attempt+1}: {e}")
            time.sleep(10)

    print(f"  [MISS] {formatted} — failed after 3 attempts")
    return None


def scrape_city(city_name: str, year: int):
    """Scrape one city for a full year, save incrementally."""
    if city_name not in CITIES:
        print(f"Unknown city: {city_name}. Choose from {list(CITIES.keys())}")
        sys.exit(1)

    geoname_id = CITIES[city_name]
    out_path   = f"data/raw/daylight_raw_{year}.csv"
    os.makedirs("data/raw", exist_ok=True)

    # Load existing data to resume if interrupted
    existing = pd.DataFrame()
    if os.path.exists(out_path):
        existing = pd.read_csv(out_path)
        already_done = set(
            existing[existing["city"] == city_name]["date"].tolist()
        )
        print(f"Resuming — {len(already_done)} days already scraped")
    else:
        already_done = set()

    driver  = make_driver()
    records = []
    start   = datetime(year, 1, 1)
    end     = datetime(year, 12, 31)
    current = start
    count   = 0

    print(f"\nScraping {city_name} for {year}...")

    try:
        while current <= end:
            date_str = current.strftime("%Y-%m-%d")

            if date_str in already_done:
                current += timedelta(days=1)
                continue

            record = scrape_day(driver, current, city_name, geoname_id)
            if record:
                records.append(record)
                count += 1

            # Save every 30 days so progress isn't lost
            if count % 30 == 0 and count > 0:
                _save(existing, records, out_path)
                print(f"  Checkpoint saved — {count} new days")

            time.sleep(3)
            current += timedelta(days=1)

    finally:
        driver.quit()
        _save(existing, records, out_path)
        print(f"\n✅ Done — {count} new days scraped for {city_name}")


def _save(existing: pd.DataFrame, new_records: list, path: str):
    """Merge new records with existing and save."""
    if not new_records:
        return
    new_df = pd.DataFrame(new_records)
    combined = pd.concat([existing, new_df]).drop_duplicates(
        subset=["date", "city"]
    ).sort_values(["city", "date"])
    combined.to_csv(path, index=False)


if __name__ == "__main__":
    year      = int(sys.argv[1]) if len(sys.argv) > 1 else 2025
    city_name = sys.argv[2]      if len(sys.argv) > 2 else "Bengaluru"
    scrape_city(city_name, year)