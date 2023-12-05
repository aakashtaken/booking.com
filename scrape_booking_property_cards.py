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

def get_last_page(soup):
    nav_elements = soup.find_all('div', attrs={'data-testid': 'pagination'})
    nav = nav_elements[-1]
    lastbutton = nav.find('ol').find_all('button', {'type': 'button'})[-1]
    lastpage = lastbutton.text.strip()
    return lastpage

def scrape_property_cards(soup):
    property_cards = soup.find_all('div',attrs={'data-testid': 'property-card-container'})
    data = pd.DataFrame(columns=['name', 'distance','href','room_type','originalprice','newprice'])
    
    for card in property_cards:
        href = card.find('a')['href'] if card.find('a') else None
        name = card.find('div', attrs={'data-testid': 'title'}).text.strip()
        div_attributes = card.find('div', attrs={'class': 'your-div-class'})  # Replace 'your-div-class' with the actual class or attribute name
        distance = card.find('span', attrs={'data-testid': 'distance'}).text.strip()
        address = card.find('span', attrs={'data-testid': 'address'}).text.strip()    
        room_type = card.find('h4', attrs={'role':'link'}).text.strip()
        wrapper = card.find('div',attrs={'data-testid':'availability-rate-wrapper'})
        pricing_elem = wrapper.find('div', attrs={'aria-expanded': 'false'})
        if pricing_elem is not None and pricing_elem.contents:
            first_content = pricing_elem.contents[0]
            originalprice = first_content.text.strip().replace("₹ ", "").replace(",", "") if hasattr(first_content, 'text') else ''
        else:
            originalprice = ''    
        newprice = card.find('span', attrs={'data-testid': 'price-and-discounted-price'}).text.strip().replace("₹ ", "").replace(",", "")
        values = [[name, distance, href, room_type, originalprice, newprice]]
        columns = ['name', 'distance', 'href', 'room_type', 'originalprice', 'newprice']
        scraped_property_cards = pd.DataFrame(values, columns=columns)
        data = pd.concat([data,scraped_property_cards])
    return data

def main():
    target_url = 'https://www.booking.com/searchresults.en-gb.html?'
    # Define parameters as a dictionary
    parameters = {
        'ss': 'New+Delhi',
        'dest_id': '-2106102',
        'dest_type': 'city',
        'checkin': '2024-02-12',
        'checkout': '2024-02-14',
        'group_adults': '2',
        'no_rooms': '1',
        'group_children': '0',
        'sb_travel_purpose': 'leisure'
    }
    
    # Concatenate parameters to the target_url
    target_url += '&' + '&'.join([f"{key}={value}" for key, value in parameters.items()])    
    # Replace the following with your actual headers if needed
    custom_headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
    'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    }
    
    print("Request sent for URL: ", target_url)
    soup = scrape_website(target_url, headers=custom_headers)

    print("Retrieve last page for search query")
    lastpage = get_last_page(soup)
    print("Last page is ", lastpage)
  
    df = pd.DataFrame(columns=['name', 'distance','href','room_type','originalprice','newprice'])
    for i in range(0,int(lastpage)+1):
        if i == 0:
            scrape_df = scrape_property_cards(soup)
            df = pd.concat([df,scrape_df],ignore_index=True)
            print("Total row count is : ",len(df.index))
        else:
            total_offset = i*25
            next_url = f"{target_url}+&offset={total_offset}"
            rant = random.randint(20, 35)
            
            time.sleep(rant)

            print("Request sent for URL: ", next_url)
            soup = scrape_website(next_url, headers=custom_headers)

            print("Scrape property cards for URL: ", next_url)
            scrape_df = scrape_property_cards(soup)
            
            df = pd.concat([df,scrape_df],ignore_index=True)
            print("Total row count is : ",len(df.index))
            
    df.to_csv('property-cards.csv',encoding = 'utf-8')

if __name__ == "__main__":
    main()