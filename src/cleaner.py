# src/cleaner.py

import pandas as pd
import numpy as np
import os
from datetime import datetime


def parse_time_to_minutes(time_str: str) -> float:
    """Convert '06:15 AM' → minutes since midnight."""
    if not isinstance(time_str, str):
        return np.nan
    time_str = time_str.strip().upper()
    # normalise missing space: "06:15AM" → "06:15 AM"
    if "AM" in time_str and " AM" not in time_str:
        time_str = time_str.replace("AM", " AM")
    if "PM" in time_str and " PM" not in time_str:
        time_str = time_str.replace("PM", " PM")
    try:
        t = datetime.strptime(time_str, "%I:%M %p")
        return t.hour * 60 + t.minute
    except ValueError:
        return np.nan


def get_season(month: int) -> str:
    """Indian meteorological seasons."""
    if month in [3, 4, 5]:
        return "Summer"
    elif month in [6, 7, 8, 9]:
        return "Rainy"
    elif month in [10, 11]:
        return "Autumn"
    else:
        return "Winter"


def clean(year: int):
    path = f"data/raw/daylight_raw_{year}.csv"
    if not os.path.exists(path):
        raise FileNotFoundError(f"Run scraper first: {path} not found")

    df = pd.read_csv(path)
    print(f"Loaded {len(df)} rows")

    # Parse dates
    df["date"] = pd.to_datetime(df["date"])

    # Calculate duration
    df["sunrise_min"]      = df["sunrise"].apply(parse_time_to_minutes)
    df["sunset_min"]       = df["sunset"].apply(parse_time_to_minutes)
    df["day_duration_hrs"] = (df["sunset_min"] - df["sunrise_min"]) / 60

    # Drop bad rows
    df = df[df["day_duration_hrs"].between(10, 15)]

    # Enrich
    df["season"]      = df["date"].dt.month.apply(get_season)
    df["month"]       = df["date"].dt.month
    df["month_name"]  = df["date"].dt.strftime("%b")
    df["day_of_year"] = df["date"].dt.dayofyear

    os.makedirs("data/processed", exist_ok=True)
    out = f"data/processed/daylight_clean_{year}.csv"
    df.to_csv(out, index=False)
    print(f"✅ Saved → {out}  ({len(df)} rows)")

    # Summary
    print("\n── Season Summary ──")
    summary = (
        df.groupby(["city", "season"])["day_duration_hrs"]
        .agg(Avg="mean", Min="min", Max="max")
        .round(2)
    )
    print(summary)
    return df


if __name__ == "__main__":
    import sys
    year = int(sys.argv[1]) if len(sys.argv) > 1 else 2025
    clean(year)