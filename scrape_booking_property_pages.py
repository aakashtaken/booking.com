import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random


def scrape_website(url, headers=None):
    # Send a GET request to the website with headers
    response = requests.get(url, headers=headers)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
    return soup

def main():
    links = pd.read_csv("dataset_price_variance.csv", encoding = 'UTF-8')
    
    custom_headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        }
    
    data = pd.DataFrame(columns=['name', 'address', 'brand', 'latlng'])
    for i in links['href']:
        print("Scrape_website for URL: ",i)
        soup = scrape_website(i, headers=custom_headers)
    
        name = soup.find('div', attrs={'data-capla-component-boundary': 'b-property-web-property-page/PropertyHeaderName'}).text.strip()
        address = soup.find('span', attrs={'class': "hp_address_subtitle js-hp_address_subtitle jq_tooltip"}).text.strip()
        
        brand_element = soup.find('p', attrs={'class': "summary hotel_meta_style"})
        brand = brand_element.text.strip().replace('Hotel chain/brand:\n', '') if brand_element else ''
        
        latlng = soup.find('a', class_='loc_block_link_underline_fix')['data-atlas-latlng']
    
        values = [[name, address, brand, latlng]]
        columns = ['name', 'address', 'brand', 'latlng']
    
        print(values)
        
        scraped_property_pages = pd.DataFrame(values, columns=columns)
        data = pd.concat([data,scraped_property_pages])
        
        rant = random.randint(10, 30)
        print("Going to sleep for ",rant," seconds")
        time.sleep(rant)
    
    data.to_csv('scraped_property_pages.csv', encoding = 'utf-8')

if __name__ == "__main__":
    main()