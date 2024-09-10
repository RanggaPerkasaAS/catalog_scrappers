from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import pandas as pd
import time

# Initialize the ChromeOptions
options = webdriver.ChromeOptions()
# Uncomment the line below to run headless (without opening a browser window)
# options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

product_links = []
base_url = 'https://www.peeba.id'
product_data = []

page_link = f"https://www.peeba.id/browse/learning-time"
driver.get(page_link)

wait = WebDriverWait(driver, 20)

wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.jss470.MuiBox-root.css-0')))
    

# Scroll to load more content
for i in range(1, 3):
    driver.execute_script(f"window.scrollTo(0, {500 * i})")
    print(f"Scrolling {i} times")
    time.sleep(1)

content = driver.page_source
soup = BeautifulSoup(content, 'html.parser')
products = soup.select('.jss470.MuiBox-root.css-0')

for product in products:
    href = product.find('a', href=True)['href']
    full_url = base_url + href
    product_links.append(full_url)
    print(full_url)