"""Facebook CPM Checker — reads CSV data and formats a Slack-ready summary."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd


def load_data(csv_path: str) -> pd.DataFrame:
    """Load CPM data from a CSV file."""
    path = Path(csv_path)
    if not path.exists():
        print(f"Error: CSV file not found at {csv_path}")
        sys.exit(1)

    df = pd.read_csv(path, parse_dates=["date"])
    required_cols = {"date", "campaign_name", "spend", "impressions", "cpm"}
    missing = required_cols - set(df.columns)
    if missing:
        print(f"Error: CSV is missing required columns: {missing}")
        print(f"Required columns: {required_cols}")
        print(f"Found columns: {set(df.columns)}")
        sys.exit(1)

    return df


def get_latest_date(df: pd.DataFrame) -> pd.Timestamp:
    """Get the most recent date in the dataset."""
    return df["date"].max()


def build_report(df: pd.DataFrame, target_date: pd.Timestamp | None = None) -> str:
    """Build a formatted CPM report for a given date.

    If target_date is None, uses the most recent date in the data.
    """
    if target_date is None:
        target_date = get_latest_date(df)

    day_data = df[df["date"] == target_date]
    if day_data.empty:
        return f"No CPM data found for {target_date.strftime('%Y-%m-%d')}."

    # Previous day for comparison
    prev_date = target_date - timedelta(days=1)
    prev_data = df[df["date"] == prev_date]

    # Today's aggregates
    total_spend = day_data["spend"].sum()
    total_impressions = day_data["impressions"].sum()
    blended_cpm = (total_spend / total_impressions * 1000) if total_impressions > 0 else 0
    total_clicks = day_data["clicks"].sum() if "clicks" in day_data.columns else None
    blended_cpc = (total_spend / total_clicks) if total_clicks and total_clicks > 0 else None

    # Previous day aggregates for delta
    delta_str = ""
    if not prev_data.empty:
        prev_spend = prev_data["spend"].sum()
        prev_impressions = prev_data["impressions"].sum()
        prev_cpm = (prev_spend / prev_impressions * 1000) if prev_impressions > 0 else 0
        cpm_delta = blended_cpm - prev_cpm
        direction = "↑" if cpm_delta > 0 else "↓" if cpm_delta < 0 else "→"
        delta_str = f" ({direction} ${abs(cpm_delta):.2f} vs yesterday)"

    date_str = target_date.strftime("%B %d, %Y")

    lines = [
        f"*Facebook Ad Performance — {date_str}*",
        "",
        f"*Blended CPM:* ${blended_cpm:.2f}{delta_str}",
        f"*Total Spend:* ${total_spend:,.2f}",
        f"*Total Impressions:* {total_impressions:,}",
    ]

    if total_clicks is not None:
        lines.append(f"*Total Clicks:* {total_clicks:,}")
    if blended_cpc is not None:
        lines.append(f"*Blended CPC:* ${blended_cpc:.2f}")

    lines.append("")
    lines.append("*By Campaign:*")

    for _, row in day_data.iterrows():
        campaign = row["campaign_name"]
        cpm = row["cpm"]
        spend = row["spend"]
        impressions = row["impressions"]

        # Compare to previous day for this campaign
        camp_delta = ""
        if not prev_data.empty:
            prev_camp = prev_data[prev_data["campaign_name"] == campaign]
            if not prev_camp.empty:
                prev_cpm_val = prev_camp.iloc[0]["cpm"]
                diff = cpm - prev_cpm_val
                d = "↑" if diff > 0 else "↓" if diff < 0 else "→"
                camp_delta = f" ({d}${abs(diff):.2f})"

        line = f"  • *{campaign}*: CPM ${cpm:.2f}{camp_delta} | Spend ${spend:,.2f} | {impressions:,} impr."
        if "clicks" in row and pd.notna(row.get("clicks")):
            line += f" | {int(row['clicks']):,} clicks"
        lines.append(line)

    # 7-day trend if enough data
    week_ago = target_date - timedelta(days=6)
    week_data = df[(df["date"] >= week_ago) & (df["date"] <= target_date)]
    if len(week_data["date"].unique()) >= 3:
        daily = week_data.groupby("date").agg({"spend": "sum", "impressions": "sum"}).reset_index()
        daily["cpm"] = daily["spend"] / daily["impressions"] * 1000
        avg_cpm = daily["cpm"].mean()
        min_cpm = daily["cpm"].min()
        max_cpm = daily["cpm"].max()
        lines.append("")
        lines.append(f"*7-Day Trend:* Avg CPM ${avg_cpm:.2f} (Low ${min_cpm:.2f} / High ${max_cpm:.2f})")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Facebook CPM Checker")
    parser.add_argument(
        "--csv",
        default="sample_cpm_data.csv",
        help="Path to CSV file with CPM data",
    )
    parser.add_argument(
        "--date",
        default=None,
        help="Date to report on (YYYY-MM-DD). Defaults to most recent date in data.",
    )
    args = parser.parse_args()

    df = load_data(args.csv)

    target = None
    if args.date:
        target = pd.Timestamp(args.date)

    report = build_report(df, target)
    print(report)


if __name__ == "__main__":
    main()
