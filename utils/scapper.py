import sys
import time
import pandas as pd

from selenium import webdriver
from datetime import datetime
from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
class DataScrapper:
	'''Class for data scrapping'''
	def __init__(self):

		self.date = datetime.today().strftime('%d-%m-%Y')
		options = webdriver.ChromeOptions()
		options.add_argument('--headless')
		options.add_argument('--no-sandbox')
		options.add_argument('--disable-dev-shm-usage')
		options.headless = True
		options.add_argument="user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
		self.driver = webdriver.Chrome(ChromeDriverManager().install())
		#self.driver.set_page_load_timeout(120)
		#self.driver.maximize_window()

	def search(self) -> None:
		self.driver.get("https://www.sharesansar.com/today-share-price")
		WebDriverWait(self.driver, 20).until(
			EC.presence_of_element_located((By.XPATH, "//input[@id='fromdate']"))
		)
		date_input = self.driver.find_element_by_xpath("//input[@id='fromdate']")
		search_btn = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@id='fromdate']")))
		date_input.send_keys(self.date)
		search_btn.click()
		if self.driver.find_elements_by_xpath("//*[contains(text(), 'Could not find floorsheet matching the search criteria')]"):

			self.driver.close()
			sys.exit()

	def get_page_table(self, df) -> pd.DataFrame:

		for data in self.driver.find_elements_by_xpath("//table[@id='headFixed']//tbody//tr"):
			
			tab_data = data.text.split(" ")
			df.loc[len(df)] = tab_data
		
		return df

	def get_scrape_data(self) -> pd.DataFrame:
		self.search()
		df = pd.DataFrame()
		count = 0
		flag = True
		while flag:
			count += 1

			print(f"Scraping Page {count}")

			try:
				column = ['S.No','Symbol','conf','Open','High','Low','Close','vwap','Vol','Prev. Close','Turnover','Trans','Diff','Range','Diff%','Range%','vwap%','120_days','180_days','52wk_high','52wk_low']
				df = pd.DataFrame(columns = column)
				df = df.append(self.get_page_table(df), ignore_index=True)
				self.driver.find_element_by_xpath("//a[@class='next']").click()
				
			except NoSuchElementException:
				print("No more pages to scrape")
				flag = False
				break
			
			time.sleep(2)
		return df
	
	def get_clean_df(self, df) -> pd.DataFrame:

		new_df = df.drop_duplicates(keep='first') 
		new_header =  ['S.No','Symbol','conf','Open','High','Low','Close','vwap','Vol','Prev. Close','Turnover','Trans','Diff','Range','Diff%','Range%','vwap%','120_days','180_days','52wk_high','52wk_low'] # grabing the first row for the header
		new_df = new_df[1:] # taking the data lower than the header row
		new_df.columns = new_header # setting the header row as the df header
		new_df.drop(["S.No"], axis=1, inplace=True)

		return new_df
