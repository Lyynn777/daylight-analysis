# src/visualizer.py

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import os

SEASON_COLORS = {
    "Summer": "#FF6B35",
    "Rainy":  "#4A90D9",
    "Autumn": "#F5A623",
    "Winter": "#7ED321",
}
SEASON_ORDER = ["Summer", "Rainy", "Autumn", "Winter"]


def load(year):
    return pd.read_csv(
        f"data/processed/daylight_clean_{year}.csv",
        parse_dates=["date"]
    )


def plot_line(df, city, year):
    """Full year line chart coloured by season."""
    d = df[df["city"] == city].sort_values("date")
    fig, ax = plt.subplots(figsize=(14, 5))
    for season, grp in d.groupby("season"):
        ax.scatter(grp["date"], grp["day_duration_hrs"],
                   color=SEASON_COLORS[season], s=10, label=season, alpha=0.9)
    ax.plot(d["date"], d["day_duration_hrs"], color="black", lw=0.5, alpha=0.3)
    ax.set_title(f"Day Duration Across {year} — {city}", fontsize=14, fontweight="bold")
    ax.set_xlabel("Date")
    ax.set_ylabel("Hours of Daylight")
    ax.legend(title="Season")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    os.makedirs("outputs", exist_ok=True)
    fig.savefig(f"outputs/01_line_{city}_{year}.png", dpi=150)
    plt.show()
    print(f"  Saved 01_line_{city}_{year}.png")


def plot_boxplot(df, city, year):
    """Season distribution box plot."""
    d = df[df["city"] == city]
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.boxplot(data=d, x="season", y="day_duration_hrs",
                order=SEASON_ORDER, palette=SEASON_COLORS, ax=ax)
    ax.set_title(f"Daylight Distribution by Season — {city} {year}",
                 fontsize=13, fontweight="bold")
    ax.set_xlabel("Season")
    ax.set_ylabel("Hours")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(f"outputs/02_boxplot_{city}_{year}.png", dpi=150)
    plt.show()
    print(f"  Saved 02_boxplot_{city}_{year}.png")


def plot_heatmap(df, year):
    """City vs Month average daylight heatmap."""
    pivot = (
        df.groupby(["city", "month"])["day_duration_hrs"]
        .mean().unstack("month")
    )
    pivot.columns = ["Jan","Feb","Mar","Apr","May","Jun",
                     "Jul","Aug","Sep","Oct","Nov","Dec"]
    fig, ax = plt.subplots(figsize=(13, 4))
    sns.heatmap(pivot, annot=True, fmt=".1f", cmap="YlOrRd",
                linewidths=0.4, ax=ax,
                cbar_kws={"label": "Avg Daylight (hrs)"})
    ax.set_title(f"Average Daylight Hours — City × Month {year}",
                 fontsize=13, fontweight="bold")
    fig.tight_layout()
    fig.savefig(f"outputs/03_heatmap_{year}.png", dpi=150)
    plt.show()
    print(f"  Saved 03_heatmap_{year}.png")


def plot_city_comparison(df, year):
    """All cities season average grouped bar."""
    grp = (df.groupby(["city", "season"])["day_duration_hrs"]
           .mean().reset_index())
    fig, ax = plt.subplots(figsize=(11, 5))
    sns.barplot(data=grp, x="season", y="day_duration_hrs",
                hue="city", order=SEASON_ORDER, ax=ax)
    ax.set_title(f"Avg Daylight by Season & City — {year}",
                 fontsize=13, fontweight="bold")
    ax.set_xlabel("Season")
    ax.set_ylabel("Avg Hours")
    ax.legend(title="City", bbox_to_anchor=(1.01, 1))
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(f"outputs/04_city_comparison_{year}.png", dpi=150)
    plt.show()
    print(f"  Saved 04_city_comparison_{year}.png")


def plot_annotated(df, city, year):
    """Line chart with solstice and equinox markers."""
    d = df[df["city"] == city].sort_values("date")
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(d["date"], d["day_duration_hrs"], color="#2C3E50", lw=1.5)
    for season, grp in d.groupby("season"):
        ax.fill_between(grp["date"], grp["day_duration_hrs"],
                        alpha=0.2, color=SEASON_COLORS[season], label=season)
    events = {
        f"{year}-06-21": "Summer\nSolstice",
        f"{year}-12-21": "Winter\nSolstice",
        f"{year}-03-20": "Spring\nEquinox",
        f"{year}-09-23": "Autumn\nEquinox",
    }
    for date_str, label in events.items():
        dt  = pd.Timestamp(date_str)
        idx = (d["date"] - dt).abs().idxmin()
        y   = d.loc[idx, "day_duration_hrs"]
        ax.axvline(dt, color="grey", linestyle="--", lw=0.8, alpha=0.6)
        ax.annotate(label, xy=(dt, y), xytext=(0, 14),
                    textcoords="offset points", ha="center", fontsize=8,
                    arrowprops=dict(arrowstyle="->", color="grey", lw=0.8))
    ax.set_title(f"Daylight with Astronomical Events — {city} {year}",
                 fontsize=13, fontweight="bold")
    ax.set_xlabel("Date")
    ax.set_ylabel("Hours")
    ax.legend(title="Season", bbox_to_anchor=(1.01, 1))
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(f"outputs/05_annotated_{city}_{year}.png", dpi=150)
    plt.show()
    print(f"  Saved 05_annotated_{city}_{year}.png")


def run_all(year=2025, city="Bengaluru"):
    print(f"\n── Generating charts for {year} ──")
    df = load(year)
    plot_line(df, city, year)
    plot_boxplot(df, city, year)
    plot_heatmap(df, year)
    plot_city_comparison(df, year)
    plot_annotated(df, city, year)
    print("\n✅ All charts saved to outputs/")


if __name__ == "__main__":
    import sys
    year = int(sys.argv[1]) if len(sys.argv) > 1 else 2025
    city = sys.argv[2] if len(sys.argv) > 2 else "Bengaluru"
    run_all(year, city)