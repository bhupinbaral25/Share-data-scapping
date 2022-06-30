import re
import pandas as pd

from utils import DataScrapper, required_columns

def save_data():
	scrapper = DataScrapper()
	df = scrapper.get_scrape_data()
	
	data = scrapper.get_clean_df(df)
	
	date = scrapper.date
	for symbol in [re.sub(r"[^A-Z]","",symbol) for symbol in list(data["Symbol"].unique())]:
		df_scrape = data[data["Symbol"]==symbol]
		df_scrape["Date"] = date
		try:
			exist_df = pd.read_csv(f"./newdata/{symbol}.csv")
			df = exist_df.append(df_scrape[required_columns])
		except FileNotFoundError:
			df = df_scrape[required_columns]
		df.to_csv(f"./newdata/{symbol}.csv", index=False)

if __name__ == "__main__":
	save_data()