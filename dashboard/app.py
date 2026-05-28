# dashboard/app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import re
import time
import random
from datetime import datetime, date, timedelta

SEASON_COLORS = {
    "Summer": "#FF6B35",
    "Rainy":  "#4A90D9",
    "Autumn": "#F5A623",
    "Winter": "#7ED321",
}
SEASON_ORDER = ["Summer", "Rainy", "Autumn", "Winter"]

CITIES = {
    "Bengaluru": 1277333,
    "Delhi":     1273294,
    "Mumbai":    1275339,
    "Chennai":   1264527,
    "Kolkata":   1275004,
}


def get_season(month: int) -> str:
    if month in [3, 4, 5]:
        return "Summer"
    elif month in [6, 7, 8, 9]:
        return "Rainy"
    elif month in [10, 11]:
        return "Autumn"
    else:
        return "Winter"


# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="India Daylight Analysis",
    page_icon="☀️",
    layout="wide"
)

st.title("☀️ India Daylight Duration Analysis")
st.markdown("Sunrise & sunset data from **drikpanchang.com** — scraped using Selenium.")

tab1, tab2 = st.tabs(["📊 Analysis Dashboard", "🔍 Live Date Lookup"])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Analysis Dashboard
# ══════════════════════════════════════════════════════════════════════════════
with tab1:

    processed_files = []
    if os.path.exists("data/processed"):
        processed_files = [
            f for f in os.listdir("data/processed")
            if f.startswith("daylight") and f.endswith(".csv")
        ]

    if not processed_files:
        st.warning("No data found yet. Use the **Live Date Lookup** tab, or run `python src/scraper.py` first.")
        st.stop()

    years = []
    for f in processed_files:
        try:
            years.append(int(f.replace(".csv", "").split("_")[-1]))
        except ValueError:
            continue
    years = sorted(set(years), reverse=True)

    st.sidebar.header("🔧 Controls")
    year = st.sidebar.selectbox("Year", years)

    df_all = None
    for fname in [
        f"daylight_clean_{year}.csv",
        f"daylight_cleaned_{year}.csv",
        f"daylight_raw_{year}.csv",
    ]:
        fpath = f"data/processed/{fname}"
        if os.path.exists(fpath):
            df_all = pd.read_csv(fpath, parse_dates=["date"])
            break

    if df_all is None:
        st.error(f"Could not load data for {year}")
        st.stop()

    if "day_duration_hrs" not in df_all.columns:
        st.error("Run cleaner first: `python src/cleaner.py`")
        st.stop()

    cities_in_data = sorted(df_all["city"].unique()) if "city" in df_all.columns else ["Bengaluru"]
    city = st.sidebar.selectbox(
        "Primary City", cities_in_data,
        index=cities_in_data.index("Bengaluru") if "Bengaluru" in cities_in_data else 0
    )
    seasons = st.sidebar.multiselect("Seasons", SEASON_ORDER, default=SEASON_ORDER)

    df      = df_all[df_all["season"].isin(seasons)] if "season" in df_all.columns else df_all
    df_city = df[df["city"] == city].sort_values("date") if "city" in df.columns else df.sort_values("date")

    # ── KPI Cards ─────────────────────────────────────────────────────────────
    st.subheader(f"📊 Key Stats — {city} {year}")
    c1, c2, c3, c4 = st.columns(4)
    longest  = df_city.loc[df_city["day_duration_hrs"].idxmax()]
    shortest = df_city.loc[df_city["day_duration_hrs"].idxmin()]
    c1.metric("☀️ Longest Day",  f"{longest['day_duration_hrs']:.2f} hrs",  str(longest["date"].date()))
    c2.metric("🌙 Shortest Day", f"{shortest['day_duration_hrs']:.2f} hrs", str(shortest["date"].date()))
    c3.metric("📅 Year Average", f"{df_city['day_duration_hrs'].mean():.2f} hrs")
    c4.metric("↕️ Annual Swing", f"{longest['day_duration_hrs'] - shortest['day_duration_hrs']:.2f} hrs")

    st.divider()

    # ── Chart 1: Full year line ────────────────────────────────────────────────
    st.subheader("📈 Full Year — Day Duration")
    fig1, ax1 = plt.subplots(figsize=(13, 4))
    if "season" in df_city.columns:
        for season, grp in df_city.groupby("season"):
            if season in seasons:
                ax1.scatter(grp["date"], grp["day_duration_hrs"],
                            color=SEASON_COLORS.get(season, "grey"),
                            s=12, label=season, alpha=0.9)
    ax1.plot(df_city["date"], df_city["day_duration_hrs"], color="black", lw=0.5, alpha=0.3)
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Hours of Daylight")
    ax1.legend(title="Season")
    ax1.grid(axis="y", alpha=0.3)
    fig1.tight_layout()
    st.pyplot(fig1)

    # ── Charts 2 & 3 ──────────────────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📦 Season Distribution")
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        plot_df = df_city[df_city["season"].isin(seasons)] if "season" in df_city.columns else df_city
        sns.boxplot(
            data=plot_df,
            x="season", y="day_duration_hrs",
            order=[s for s in SEASON_ORDER if s in seasons],
            palette=SEASON_COLORS, ax=ax2
        )
        ax2.set_xlabel("Season")
        ax2.set_ylabel("Hours")
        ax2.grid(axis="y", alpha=0.3)
        fig2.tight_layout()
        st.pyplot(fig2)

    with col2:
        st.subheader("🌡️ Month-wise Average")
        monthly = df_city.groupby("month")["day_duration_hrs"].mean().reset_index()
        month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        monthly["month_name"] = monthly["month"].apply(lambda x: month_names[x - 1])
        fig3, ax3 = plt.subplots(figsize=(7, 4))
        ax3.bar(monthly["month_name"], monthly["day_duration_hrs"], color="#4A90D9", alpha=0.8)
        ax3.set_xlabel("Month")
        ax3.set_ylabel("Avg Hours")
        ax3.grid(axis="y", alpha=0.3)
        fig3.tight_layout()
        st.pyplot(fig3)

    # ── Raw data ───────────────────────────────────────────────────────────────
    with st.expander("🔍 View Raw Data"):
        show_cols = [c for c in ["date","city","season","sunrise","sunset","day_duration_hrs"] if c in df_city.columns]
        st.dataframe(df_city[show_cols].reset_index(drop=True), use_container_width=True)
        st.download_button(
            "⬇️ Download CSV",
            df_city.to_csv(index=False).encode(),
            file_name=f"daylight_{city}_{year}.csv",
            mime="text/csv"
        )

    st.caption("Data source: drikpanchang.com | Built with Streamlit, Matplotlib, Seaborn")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Live Date Lookup
# ══════════════════════════════════════════════════════════════════════════════
with tab2:

    st.subheader("🔍 Live Sunrise / Sunset Lookup")
    st.markdown("Fetch live data directly from drikpanchang.com for any date or range.")
    st.info("💡 Results are cached locally — repeated lookups are instant.")

    # ── Controls ──────────────────────────────────────────────────────────────
    col_a, col_b = st.columns(2)
    with col_a:
        lookup_city = st.selectbox("City", list(CITIES.keys()), key="lookup_city")
    with col_b:
        mode = st.radio("Mode", ["Single Date", "Date Range"], horizontal=True)

    if mode == "Single Date":
        selected_date = st.date_input(
            "Select Date",
            value=date.today(),
            min_value=date(2000, 1, 1),
            max_value=date(2030, 12, 31)
        )
        date_list = [selected_date]
    else:
        col_s, col_e = st.columns(2)
        with col_s:
            start_date = st.date_input(
                "Start Date",
                value=date(2025, 1, 1),
                min_value=date(2000, 1, 1),
                max_value=date(2030, 12, 31),
                key="start"
            )
        with col_e:
            end_date = st.date_input(
                "End Date",
                value=date(2025, 1, 31),
                min_value=date(2000, 1, 1),
                max_value=date(2030, 12, 31),
                key="end"
            )

        if end_date < start_date:
            st.error("End date must be after start date.")
            st.stop()

        total_days = (end_date - start_date).days + 1
        if total_days > 60:
            st.warning(
                f"⚠️ {total_days} days selected — estimated time: "
                f"~{total_days * 3 // 60} mins. Consider a smaller range."
            )

        date_list = [start_date + timedelta(days=i) for i in range(total_days)]

    # ── Fetch button ───────────────────────────────────────────────────────────
    if st.button("🚀 Fetch Data", type="primary"):

        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from webdriver_manager.chrome import ChromeDriverManager
        except ImportError:
            st.error("Selenium not installed. Run: `pip install selenium webdriver-manager`")
            st.stop()

        # ── Driver ────────────────────────────────────────────────────────────
        @st.cache_resource
        def get_driver():
            opts = webdriver.ChromeOptions()
            opts.add_argument("--headless")
            opts.add_argument("--no-sandbox")
            opts.add_argument("--disable-dev-shm-usage")
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

        driver = get_driver()

        # ── Local cache ───────────────────────────────────────────────────────
        cache_path = "data/processed/live_lookup_cache.csv"
        os.makedirs("data/processed", exist_ok=True)

        if os.path.exists(cache_path):
            cache_df = pd.read_csv(cache_path)
        else:
            cache_df = pd.DataFrame(columns=["date","city","sunrise","sunset","day_duration_hrs","season"])

        # ── Loop over dates ───────────────────────────────────────────────────
        geoname_id = CITIES[lookup_city]
        results    = []
        errors     = []
        progress   = st.progress(0, text="Starting...")
        status     = st.empty()

        for i, d in enumerate(date_list):
            formatted_iso  = d.strftime("%Y-%m-%d")
            formatted_site = d.strftime("%d/%m/%Y")

            # Check cache first
            if not cache_df.empty:
                match = cache_df[
                    (cache_df["date"] == formatted_iso) &
                    (cache_df["city"] == lookup_city)
                ]
                if not match.empty:
                    results.append(match.iloc[0].to_dict())
                    progress.progress(
                        (i + 1) / len(date_list),
                        text=f"✅ Cached: {formatted_iso}"
                    )
                    continue

            # Not in cache — fetch from website
            url = (
                f"https://www.drikpanchang.com/panchang/day-panchang.html"
                f"?date={formatted_site}&geoname-id={geoname_id}"
            )
            status.text(f"Fetching {formatted_site} ({i+1}/{len(date_list)})...")
            progress.progress(
                (i + 1) / len(date_list),
                text=f"Fetching {formatted_site}..."
            )

            fetched = False
            for attempt in range(3):
                try:
                    driver.get(url)
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    time.sleep(random.uniform(2, 3))
                    body = driver.find_element(By.TAG_NAME, "body").text

                    if len(body.strip()) < 100:
                        time.sleep(5)
                        continue

                    sr = re.search(r"Sunrise\s*([0-9]{1,2}:[0-9]{2}\s*[APap][Mm])", body)
                    ss = re.search(r"Sunset\s*([0-9]{1,2}:[0-9]{2}\s*[APap][Mm])",  body)

                    if sr and ss:
                        sunrise = sr.group(1).strip()
                        sunset  = ss.group(1).strip()

                        try:
                            sr_dt    = datetime.strptime(sunrise.upper(), "%I:%M %p")
                            ss_dt    = datetime.strptime(sunset.upper(),  "%I:%M %p")
                            duration = round((ss_dt - sr_dt).total_seconds() / 3600, 2)
                        except Exception:
                            duration = None

                        row = {
                            "date":             formatted_iso,
                            "city":             lookup_city,
                            "sunrise":          sunrise,
                            "sunset":           sunset,
                            "day_duration_hrs": duration,
                            "season":           get_season(d.month),
                        }
                        results.append(row)

                        # Save to cache immediately
                        cache_df = pd.concat(
                            [cache_df, pd.DataFrame([row])]
                        ).drop_duplicates(subset=["date","city"])
                        cache_df.to_csv(cache_path, index=False)

                        fetched = True
                        break

                    else:
                        time.sleep(random.uniform(3, 6))

                except Exception as e:
                    if attempt == 2:
                        errors.append({"date": formatted_site, "reason": str(e)})
                    time.sleep(5)

            if not fetched and not any(e["date"] == formatted_site for e in errors):
                errors.append({"date": formatted_site, "reason": "Times not found after 3 attempts"})

            time.sleep(random.uniform(2, 3))

        progress.empty()
        status.empty()

        # ── Show results ───────────────────────────────────────────────────────
        if results:
            df_result = pd.DataFrame(results)
            df_result["date"] = pd.to_datetime(df_result["date"])

            st.success(f"✅ {len(results)} days fetched successfully!")

            if len(results) == 1:
                # Single date card
                row = results[0]
                st.markdown(f"""
| | |
|---|---|
| 📅 Date | **{row['date']}** |
| 🌆 City | **{row['city']}** |
| 🌅 Sunrise | **{row['sunrise']}** |
| 🌇 Sunset | **{row['sunset']}** |
| ⏱️ Day Duration | **{row['day_duration_hrs']} hrs** |
| 🍂 Season | **{row['season']}** |
                """)
            else:
                # Range KPIs
                r1, r2, r3, r4 = st.columns(4)
                r1.metric("📅 Days Fetched", len(results))
                r2.metric("☀️ Avg Daylight",  f"{df_result['day_duration_hrs'].mean():.2f} hrs")
                r3.metric("🌅 Longest Day",
                          f"{df_result['day_duration_hrs'].max():.2f} hrs",
                          str(df_result.loc[df_result['day_duration_hrs'].idxmax(), 'date'].date()))
                r4.metric("🌃 Shortest Day",
                          f"{df_result['day_duration_hrs'].min():.2f} hrs",
                          str(df_result.loc[df_result['day_duration_hrs'].idxmin(), 'date'].date()))

                # Chart
                fig, ax = plt.subplots(figsize=(12, 4))
                for season, grp in df_result.groupby("season"):
                    ax.scatter(grp["date"], grp["day_duration_hrs"],
                               color=SEASON_COLORS.get(season, "grey"), s=20, label=season)
                ax.plot(df_result["date"], df_result["day_duration_hrs"],
                        color="black", lw=0.6, alpha=0.4)
                ax.set_xlabel("Date")
                ax.set_ylabel("Hours")
                ax.set_title(f"Daylight Duration — {lookup_city}")
                ax.legend(title="Season")
                ax.grid(axis="y", alpha=0.3)
                fig.tight_layout()
                st.pyplot(fig)

            # Data table
            st.dataframe(df_result, use_container_width=True)

            # Download
            st.download_button(
                "⬇️ Download This Data",
                df_result.to_csv(index=False).encode(),
                file_name=f"daylight_{lookup_city}_{date_list[0]}_{date_list[-1]}.csv",
                mime="text/csv"
            )

            # Save to processed folder
            st.divider()
            if st.button("💾 Save to processed data folder"):
                year_val = date_list[0].year
                out_path = f"data/processed/daylight_clean_{year_val}.csv"
                if os.path.exists(out_path):
                    existing = pd.read_csv(out_path, parse_dates=["date"])
                    combined = (
                        pd.concat([existing, df_result])
                        .drop_duplicates(subset=["date","city"])
                        .sort_values("date")
                    )
                    combined.to_csv(out_path, index=False)
                    st.success(f"✅ Appended → {out_path} ({len(combined)} rows total)")
                else:
                    df_result.to_csv(out_path, index=False)
                    st.success(f"✅ Saved → {out_path} ({len(df_result)} rows)")

        if errors:
            with st.expander(f"⚠️ {len(errors)} dates failed"):
                st.dataframe(pd.DataFrame(errors), use_container_width=True)