from utils import DataScrapper

def save_data():

    scrapper = DataScrapper()
    df = scrapper.clean_df()
    df.to_csv(f"data/{scrapper.date}.csv", index=False)

