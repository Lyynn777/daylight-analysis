"""
Run the full pipeline:
  python main.py            → scrape + clean + visualize 2025
  python main.py 2024       → any year
  python main.py 2025 Delhi → specific city as primary
"""
import sys
from src.scraper    import scrape_year
from src.cleaner    import clean
from src.visualizer import run_all

if __name__ == "__main__":
    year = int(sys.argv[1]) if len(sys.argv) > 1 else 2025
    city = sys.argv[2]      if len(sys.argv) > 2 else "Bengaluru"

    print(f"\n{'='*50}")
    print(f"  DAYLIGHT ANALYSIS PIPELINE — {year}")
    print(f"{'='*50}\n")

    print("STEP 1 — Scraping data...")
    scrape_year(year)

    print("\nSTEP 2 — Cleaning data...")
    clean(year)

    print("\nSTEP 3 — Generating visualizations...")
    run_all(year, city)

    print(f"\n{'='*50}")
    print("  PIPELINE COMPLETE ✅")
    print(f"  Run dashboard:  streamlit run dashboard/app.py")
    print(f"{'='*50}\n")