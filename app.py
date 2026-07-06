import re
from pathlib import Path

import pandas as pd

from utils import DataScrapper, required_columns

DATA_DIR = Path("./newdata")


def save_data() -> None:
    scrapper = DataScrapper()
    try:
        data = scrapper.get_clean_df(scrapper.get_scrape_data())
    finally:
        scrapper.quit()

    if data.empty:
        print("No data scraped; nothing to save.")
        return

    data["Date"] = scrapper.date

    missing = set(required_columns) - set(data.columns)
    if missing:
        raise RuntimeError(f"Site table is missing expected columns: {sorted(missing)}")

    DATA_DIR.mkdir(exist_ok=True)

    for symbol in data["Symbol"].unique():
        file_name = re.sub(r"[^A-Z0-9]", "", str(symbol).upper())
        if not file_name:
            continue
        df_symbol = data.loc[data["Symbol"] == symbol, required_columns]
        path = DATA_DIR / f"{file_name}.csv"
        if path.exists():
            existing = pd.read_csv(path)
            # Re-runs on the same day replace that day's rows instead of
            # appending duplicates.
            existing = existing[existing["Date"] != scrapper.date]
            df_symbol = pd.concat([existing, df_symbol], ignore_index=True)
        df_symbol.to_csv(path, index=False)

    print(f"Saved {len(data)} rows across {data['Symbol'].nunique()} symbols.")


if __name__ == "__main__":
    save_data()
