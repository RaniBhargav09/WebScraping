import csv
import requests
from bs4 import BeautifulSoup
import time

def scrape_product_listing_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    products = []
    listings = soup.find_all('div', {'data-component-type': 's-search-result'})

    for listing in listings:
        product_url = 'https://www.amazon.in' + listing.find('a', {'class': 'a-link-normal'})['href']
        product_name = listing.find('span', {'class': 'a-size-medium'}).text.strip()
        product_price = listing.find('span', {'class': 'a-offscreen'}).text.strip()
        product_rating = listing.find('span', {'class': 'a-icon-alt'}).text.strip().split()[0]
        product_reviews = listing.find('span', {'class': 'a-size-base'}).text.strip().split()[0]

        products.append({
            'Product URL': product_url,
            'Product Name': product_name,
            'Product Price': product_price,
            'Rating': product_rating,
            'Number of Reviews': product_reviews
        })

    return products

def scrape_product_details_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    asin = soup.find('th', string='ASIN').find_next('td').text.strip()
    description = soup.find('div', {'id': 'productDescription'}).text.strip()
    manufacturer = soup.find('a', {'id': 'bylineInfo'}).text.strip()

    return {
        'ASIN': asin,
        'Description': description,
        'Manufacturer': manufacturer
    }

def scrape_amazon_products():
    base_url = 'https://www.amazon.in/s'
    query_params = {
        'k': 'bags',
        'crid': '2M096C61O4MLT',
        'qid': '1653308124',
        'sprefix': 'ba,aps,283',
        'ref': 'sr_pg_'
    }

    all_products = []
    page_count = 0

    while page_count < 20:  # Scrape 20 pages
        page_count += 1
        query_params['ref'] = 'sr_pg_' + str(page_count)
        url = base_url + '?' + '&'.join(f'{key}={value}' for key, value in query_params.items())
        products = scrape_product_listing_page(url)
        all_products.extend(products)

    scraped_data = []

    for product in all_products[:200]:  # Scrape 200 product details
        product_url = product['Product URL']
        product_details = scrape_product_details_page(product_url)
        product.update(product_details)
        scraped_data.append(product)
        time.sleep(2)  # Add a delay to be respectful of the website's terms of service

    # Export data to CSV
    keys = ['Product URL', 'Product Name', 'Product Price', 'Rating', 'Number of Reviews', 'ASIN', 'Description', 'Manufacturer']
    with open('scraped_data.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writeheader()
        writer.writerows(scraped_data)

scrape_amazon_products()