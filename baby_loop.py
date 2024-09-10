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

# Scraping the product links
for j in range(1, 65):
    page_link = f'https://baby-loop.com/shop/page/{j}/'
    driver.get(page_link)

    wait = WebDriverWait(driver, 20)

    try:
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.product-small.col.has-hover.product.type-product')))
    except TimeoutException:
        print(f"Timed out waiting for page {j} to load")
        continue

    content = driver.page_source
    soup = BeautifulSoup(content, 'html.parser')
    products = soup.select('.product-small.col.has-hover.product.type-product')

    for product in products:
        href = product.find('a', href=True)['href']
        product_links.append(href)

# Scraping product details
product_detail = []

for product_link in product_links:
    driver.get(product_link)
    content = driver.page_source
    soup = BeautifulSoup(content, 'html.parser')

    # Corrected selectors
    product_name = soup.find('h1', class_="product-title product_title entry-title")
    price_wrapper = soup.find('div', class_="price-wrapper")
    sku = soup.find('span', class_="sku")
    description_div = soup.find('div', class_='woocommerce-Tabs-panel--description')

    # Target the specific div for the thumbnails
    thumbnails_div = soup.find('div', class_='product-thumbnails thumbnails slider row row-small row-slider slider-nav-small small-columns-4 flickity-enabled is-draggable')
    
    image_urls = []
    
    # Check if the thumbnails div exists
    if thumbnails_div:
        # Extract all image URLs from the thumbnails div
        image_tags = thumbnails_div.find_all('img')
        image_urls = [img['src'] for img in image_tags]
    else:
        # If thumbnails div does not exist, use the main product image
        main_image_tag = soup.find('img', class_='wp-post-image skip-lazy')
        if main_image_tag:
            image_urls = [main_image_tag['src']]

    # Extracting text content
    product_name = product_name.get_text(strip=True) if product_name else "N/A"
    
    # Extract price
    if price_wrapper:
        price_amount = price_wrapper.find('span', class_="woocommerce-Price-amount")
        currency_symbol = price_wrapper.find('span', class_="woocommerce-Price-currencySymbol")
        price = f"{currency_symbol.get_text(strip=True)} {price_amount.get_text(strip=True)}" if price_amount else "N/A"
    else:
        price = "N/A"
    
    sku = sku.get_text(strip=True) if sku else "N/A"
    description_text = description_div.get_text(separator='\n', strip=True) if description_div else "N/A"

    # Create a dictionary for each product's details, including individual image URLs
    product_data = {
        'product_link': product_link,
        'product_name': product_name,
        'price': price,
        'sku': sku,
        'description': description_text,
    }

    # Add image URLs to the dictionary, each in a separate key (column)
    for i, url in enumerate(image_urls):
        product_data[f'image_url_{i+1}'] = url

    product_detail.append(product_data)

driver.quit()

# Convert the list of dictionaries into a DataFrame
df = pd.DataFrame(product_detail)

# Save the DataFrame to a CSV file
df.to_csv('product_detail.csv', index=False)

print("Scraping completed and saved to 'product_detail.csv'.")
