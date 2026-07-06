# NEPSE Share Data Scraper

Automated daily scraper for Nepal Stock Exchange (NEPSE) share prices.
A GitHub Actions workflow scrapes [ShareSansar's today share price page](https://www.sharesansar.com/today-share-price)
every trading day and commits the data to this repository — one CSV file per stock symbol.

## How it works

1. A scheduled GitHub Actions workflow runs daily at **11:15 UTC (17:00 NPT)**, after market close.
2. The scraper opens the ShareSansar share-price table in headless Chrome (Selenium).
3. If there is no floorsheet for today (weekend/market holiday), it exits cleanly without committing.
4. Otherwise it appends one row per symbol to `newdata/<SYMBOL>.csv` and pushes the commit.

Re-running on the same day is safe: that day's rows are replaced, never duplicated.

## Data

Each file in `newdata/` holds the full daily history for one symbol:

| Column | Description |
|--------|-------------|
| `Symbol` | Stock ticker (e.g. `NABIL`) |
| `Open` | Opening price |
| `High` | Day high |
| `Low` | Day low |
| `Vol` | Traded volume (shares) |
| `Close` | Closing price |
| `Prev. Close` | Previous day's close |
| `Turnover` | Traded value (NPR) |
| `Date` | Trading date, `DD-MM-YYYY` |

Example (`newdata/NABIL.csv`):

```csv
Symbol,Open,High,Low,Vol,Close,Prev. Close,Turnover,Date
NABIL,640.00,640.00,621.00,"103,484.00",623.60,639.00,"65,026,439.50",25-07-2023
```

## Project structure

```text
.
├── app.py                                  # Entry point: scrape, clean, save per-symbol CSVs
├── utils/
│   ├── __init__.py                         # Exposes DataScrapper and required_columns
│   └── scapper.py                          # Selenium scraper for ShareSansar
├── newdata/                                # One CSV per symbol (the dataset)
├── requirements.txt
└── .github/workflows/data_scrape_action.yaml
```

## Running locally

Requires Python 3.12 and Google Chrome (Selenium Manager downloads the matching
chromedriver automatically).

```bash
pip install -r requirements.txt
python app.py
```

The scraper only saves data when ShareSansar has a floorsheet for the current
date in Nepal (Asia/Kathmandu). On non-trading days it prints a notice and exits.

You can also trigger the workflow manually from the **Actions** tab
(`Nepse data auto scraping` → *Run workflow*).

## Future plans

With a growing daily history per symbol, this dataset can feed a machine
learning pipeline to forecast share prices.

## Contributing

Fork the project, add a feature, and open a pull request.

## Author

Bhupin Baral — bhupinbaral.729@gmail.com
