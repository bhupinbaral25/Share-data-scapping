import sys
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

SHARE_PRICE_URL = "https://www.sharesansar.com/today-share-price"
NEPAL_TZ = ZoneInfo("Asia/Kathmandu")
PAGE_LOAD_TIMEOUT = 120
WAIT_TIMEOUT = 30
PAGE_DELAY_SECONDS = 2
MAX_PAGES = 100


class DataScrapper:
    """Scrapes today's share prices from sharesansar.com."""

    def __init__(self) -> None:
        self.date = datetime.now(NEPAL_TZ).strftime("%d-%m-%Y")
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        # Selenium Manager (bundled with Selenium 4.6+) resolves the
        # matching chromedriver automatically.
        self.driver = webdriver.Chrome(options=options)
        self.driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)

    def open_today_page(self) -> None:
        """Load the share-price page and exit cleanly if today has no data."""
        self.driver.get(SHARE_PRICE_URL)
        WebDriverWait(self.driver, WAIT_TIMEOUT).until(
            EC.presence_of_element_located(
                (By.XPATH, "//table[@id='headFixed']//tbody//tr")
            )
        )
        page_date = self.driver.find_element(By.ID, "fromdate").get_attribute("value")
        today = datetime.now(NEPAL_TZ).strftime("%Y-%m-%d")
        if page_date and page_date != today:
            print(
                f"No floorsheet for today ({today}); "
                f"latest available is {page_date}. Market likely closed."
            )
            sys.exit(0)

    def get_table_header(self) -> list:
        """Read the column names from the live table header."""
        return [
            th.text.strip()
            for th in self.driver.find_elements(
                By.XPATH, "//table[@id='headFixed']//thead//tr//th"
            )
        ]

    def get_page_rows(self, expected_cells: int) -> list:
        """Return the current page's table rows as lists of cell texts."""
        rows = []
        for row in self.driver.find_elements(
            By.XPATH, "//table[@id='headFixed']//tbody//tr"
        ):
            cells = [cell.text.strip() for cell in row.find_elements(By.TAG_NAME, "td")]
            if len(cells) == expected_cells:
                rows.append(cells)
            elif cells:
                print(f"Skipping row with {len(cells)} cells: {cells[:3]}...")
        return rows

    def get_scrape_data(self) -> pd.DataFrame:
        self.open_today_page()
        header = self.get_table_header()
        if not header:
            raise RuntimeError("Could not read table header from page")
        all_rows = []
        for page in range(1, MAX_PAGES + 1):
            print(f"Scraping page {page}")
            all_rows.extend(self.get_page_rows(len(header)))
            try:
                # The anchor's class becomes "next disabled" on the last
                # page, so the exact-class match stops the loop there.
                next_button = self.driver.find_element(By.XPATH, "//a[@class='next']")
            except NoSuchElementException:
                print("No more pages to scrape")
                break
            try:
                next_button.click()
            except ElementClickInterceptedException:
                self.driver.execute_script("arguments[0].click();", next_button)
            time.sleep(PAGE_DELAY_SECONDS)
        return pd.DataFrame(all_rows, columns=header)

    def get_clean_df(self, df: pd.DataFrame) -> pd.DataFrame:
        new_df = df.drop_duplicates(keep="first").copy()
        new_df.drop(columns=["S.No"], errors="ignore", inplace=True)
        return new_df

    def quit(self) -> None:
        self.driver.quit()
