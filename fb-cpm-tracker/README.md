# Facebook CPM Tracker

Daily Facebook ad CPM checker that reads from a CSV file and sends a formatted summary to Slack.

## How It Works

1. You export your Facebook Ads data as a CSV (or update the CSV manually)
2. A scheduled Devin session runs daily, reads the CSV, and posts the CPM summary to Slack

## CSV Format

The CSV must include these columns:

| Column | Required | Description |
|--------|----------|-------------|
| `date` | Yes | Date (YYYY-MM-DD) |
| `campaign_name` | Yes | Campaign name |
| `spend` | Yes | Daily spend ($) |
| `impressions` | Yes | Number of impressions |
| `cpm` | Yes | Cost per 1,000 impressions |
| `clicks` | No | Number of clicks |
| `cpc` | No | Cost per click |

See `sample_cpm_data.csv` for an example.

## Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Run with sample data (reports most recent date)
python cpm_checker.py

# Run with your own CSV
python cpm_checker.py --csv /path/to/your/data.csv

# Report for a specific date
python cpm_checker.py --csv data.csv --date 2026-04-30
```

## Output

The script outputs a Slack-formatted message with:
- Blended CPM with day-over-day delta
- Total spend, impressions, clicks, CPC
- Per-campaign breakdown with deltas
- 7-day trend (avg/low/high CPM)

## Scheduled Delivery

A Devin scheduled session runs daily and posts the report to Slack, pinging @Eli.
