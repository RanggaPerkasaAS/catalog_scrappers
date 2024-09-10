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
base_url = 'https://desty.store'
product_data = []

for j in range(1,9) :
    page_link = f"https://desty.store/mojospace/products?CollectionItem=%7B%22id%22%3A%22%22,%22name%22%3A%22Semua%20Produk%22%7D&activePage=products&sortValue=RELEASE_DATE&searchContent=&viewIndex={j}&tab=AllProduct"
    driver.get(page_link)

    wait = WebDriverWait(driver, 20)

    try:
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.row.q-col-gutter-md.customSpacing')))
    except TimeoutException:
        print(f"Timed out waiting for page {j} to load")
        continue

    # Scroll to load more content
    for i in range(1, 4):
        driver.execute_script(f"window.scrollTo(0, {500 * i})")
        print(f"Scrolling {i} times")
        time.sleep(1)

    content = driver.page_source
    soup = BeautifulSoup(content, 'html.parser')
    products = soup.select('.col-xs-6.card.col-sm-3')

    for product in products:
        href = product.find('a', href=True)['href']
        full_url = base_url + href
        product_links.append(full_url)
        print(full_url)


for product_link in product_links:
    driver.get(product_link)

    content = driver.page_source
    soup = BeautifulSoup(content, 'html.parser')

    # Extracting and cleaning the product name
    product_name_tag = soup.find('h1', class_="productName apply-font-storeHeading pcName header-color")
    product_name = product_name_tag.get_text(strip=True) if product_name_tag else "N/A"

    # Extracting and cleaning the price
    price_tag = soup.find('div', class_="col-9 priceLine bottomLine header-color")
    price = price_tag.get_text(strip=True) if price_tag else "N/A"

    # Extracting and cleaning the description
    description_div = soup.find('div', class_='descriptionV2')
    product_description = description_div.get_text(separator="\n").strip() if description_div else "No description available"

    thumbnails_div = soup.find('div', class_='carousel-pagination')

    image_urls = []

    # Check if the thumbnails div exists
    if thumbnails_div:
        # Extract all image URLs from the thumbnails div
        image_tags = thumbnails_div.find_all('img')
        image_urls = [img['src'] for img in image_tags]
    else:
        # If thumbnails div does not exist, use the main product image
        main_image_tag = soup.find('img', class_='imgItem cursor-pointer')
        if main_image_tag:
            image_urls = [main_image_tag['src']]

    # Collect the data in a dictionary
    product_info = {
        'Product Name': product_name,
        'Price': price,
        'Description': product_description,
        'URL': product_link
    }
    
    # Add image URLs to the dictionary with separate keys
    for i, url in enumerate(image_urls):
        product_info[f'image_url_{i+1}'] = url

    # Append the product_info dictionary to the list
    product_data.append(product_info)

# Convert the list of dictionaries into a pandas DataFrame
df = pd.DataFrame(product_data)

# Optionally, save to a CSV file
df.to_csv('product_details_cleaned.csv', index=False)

# Print the collected data
print(df)

# Close the browser
driver.quit()