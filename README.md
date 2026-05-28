# ☀️ India Daylight Duration Analysis

> An end-to-end data science project that scrapes, cleans, analyzes, and visualizes
> sunrise & sunset patterns using real data from drikpanchang.com

<br>

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-Scraping-green?style=for-the-badge&logo=selenium&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Automated-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)

<br>

---

## 🔍 About the Project

This project answers a simple question:

> **How does the duration of daylight change across seasons in Indian cities — and does latitude play a role?**

To answer it, I built a complete data pipeline from scratch:

1. **Scraped** daily sunrise and sunset times for 365 days across 5 cities from [drikpanchang.com](https://www.drikpanchang.com) using Selenium — a JavaScript-rendered website that required browser automation since BeautifulSoup alone could not access the data.

2. **Cleaned and engineered** features including day duration, season labels, monthly averages, and day-of-year numbers using Pandas.

3. **Analyzed** seasonal patterns and compared how latitude affects the annual swing in daylight hours across Bengaluru, Delhi, Mumbai, Chennai, and Kolkata.

4. **Visualized** the findings using Matplotlib and Seaborn across 5 chart types.

5. **Deployed** an interactive Streamlit dashboard with a Live Date Lookup feature that lets users fetch sunrise/sunset data for any date on demand.

6. **Automated** the entire scraping pipeline using GitHub Actions, which runs on a schedule and commits fresh data back to the repository.

<br>

---

## 📁 Project Structure

```
daylight-analysis/
│
├── .github/
│   └── workflows/
│       └── scrape.yml              ← GitHub Actions automation
│
├── data/
│   ├── raw/                        ← Raw scraped CSVs (gitignored)
│   └── processed/                  ← Cleaned CSVs with engineered features
│
├── src/
│   ├── scraper.py                  ← Selenium scraper (local use)
│   ├── scraper_actions.py          ← Selenium scraper (GitHub Actions)
│   ├── cleaner.py                  ← Data cleaning + feature engineering
│   └── visualizer.py              ← Static chart generation
│
├── dashboard/
│   └── app.py                      ← Streamlit interactive dashboard
│
├── outputs/                        ← Saved chart images
│
├── .gitignore
├── requirements.txt
└── README.md
```

<br>

---

## 🛠️ Tech Stack

| Tool | Version | Purpose |
|------|---------|---------|
| **Python** | 3.11 | Core language |
| **Selenium** | 4.44 | Browser automation for JS-rendered scraping |
| **webdriver-manager** | latest | Automatic ChromeDriver management |
| **BeautifulSoup4** | 4.14 | HTML parsing |
| **Pandas** | 2.x | Data cleaning and feature engineering |
| **Matplotlib** | 3.x | Static visualizations |
| **Seaborn** | 0.13 | Statistical chart styling |
| **Streamlit** | 1.57 | Interactive dashboard and deployment |

<br>

---

## ⚙️ How to Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/Lyynn777/daylight-analysis.git
cd daylight-analysis
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Scrape data

```bash
# Scrape Bengaluru for 2025 (takes ~30 minutes)
python src/scraper.py 2025

# Or use the Live Lookup tab in the dashboard for specific dates
```

### 4. Clean the data

```bash
python src/cleaner.py 2025
```

### 5. Generate static charts

```bash
python src/visualizer.py 2025
```

### 6. Launch the dashboard

```bash
streamlit run dashboard/app.py
```

<br>

> ⚠️ **Note:** Chrome must be installed on your machine for Selenium to work.
> The scraper uses `webdriver-manager` which downloads ChromeDriver automatically.

<br>

---

## 🖥️ Dashboard Features

### Tab 1 — Analysis Dashboard

| Feature | Description |
|---------|-------------|
| 📊 KPI Cards | Longest day, shortest day, yearly average, annual swing |
| 📈 Full Year Line Chart | Day duration plotted across all 365 days, colour-coded by season |
| 📦 Season Boxplot | Distribution of daylight hours per season with outliers |
| 🌡️ Month-wise Bar Chart | Average daylight by month |
| 🔍 Raw Data Table | Filterable table with download option |
| 🎛️ Sidebar Controls | Filter by year, city, and season |

<br>

### Tab 2 — Live Date Lookup

| Feature | Description |
|---------|-------------|
| 📅 Single Date | Fetch sunrise, sunset, duration for any specific date |
| 📆 Date Range | Fetch data for a custom range with progress tracking |
| ⚡ Local Cache | Already-fetched dates load instantly without hitting the website |
| 📥 Download | Export any lookup result as CSV |
| 💾 Save to Dataset | Append live results to the main processed dataset |
| 🔁 Retry Logic | Automatically retries failed requests up to 3 times |

<br>

---

## 🤖 Automated Pipeline

This project uses **GitHub Actions** to run the scraper automatically on a schedule. (currently under progress)

```
Every 1st of the month at 6:00 AM IST
            ↓
GitHub Actions spins up Ubuntu runner
            ↓
Installs Chrome + Python dependencies
            ↓
Runs scraper → cleaner → saves CSV
            ↓
Commits updated data back to repository
            ↓
Streamlit Cloud auto-redeploys dashboard
```

### Manual trigger

You can also trigger the scraper manually from the GitHub UI:

```
Repository → Actions → Scrape Daylight Data → Run workflow
```

Enter a year and city name, click **Run workflow** — done.

<br>

---

## 🧠 What I Learned

**Technical skills:**

- How to scrape JavaScript-rendered websites using Selenium when BeautifulSoup returns empty results — including inspecting network requests, JS variables (`dpTimeContext`, `dpPgContext`), and DOM structure to understand how a page actually loads its data
- How to build a resilient scraper with retry logic, rate-limit handling, and incremental checkpointing so progress is never lost
- Feature engineering with Pandas: converting time strings to durations, assigning seasons, extracting temporal features
- Building multi-tab Streamlit dashboards with live scraping, caching, and data persistence
- Setting up GitHub Actions CI/CD workflows with scheduled jobs and manual triggers

**Data insights:**

- Latitude is the dominant factor in seasonal daylight variation — cities closer to the equator have a flatter annual curve
- drikpanchang.com is a fully server-side rendered site — all data is baked into the initial HTML, not loaded via AJAX
- Indian meteorological seasons do not align neatly with astronomical solstices — the monsoon (June–September) cuts across what would otherwise be a simple summer peak

<br>

---

## 🔮 Future Improvements

- [ ] Add all 5 cities to the automated scraper pipeline
- [ ] Correlate daylight hours with temperature and rainfall data (IMD open data)
- [ ] Build a year-over-year comparison view (2020–2025)
- [ ] Add solar energy potential estimation using daylight duration as a proxy
- [ ] Expand to international cities for global latitude comparison
- [ ] Add dark mode support to the Streamlit dashboard

<br>

---

## 📦 Requirements

```
selenium==4.44.0
webdriver-manager
pandas
matplotlib
seaborn
streamlit
beautifulsoup4
```

Install all at once:

```bash
pip install -r requirements.txt
```

<br>

---

## ⭐ If you found this project useful, please consider giving it a star!

---

*Data source: [drikpanchang.com](https://www.drikpanchang.com) — Panchang and astronomical data for India*
