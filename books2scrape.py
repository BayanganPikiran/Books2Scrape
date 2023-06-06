import gspread
from gspread_dataframe import set_with_dataframe
from google.oauth2.service_account import Credentials
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv
import os

SHEET_KEY = '1qPEMGkScpA8OCOgqjUhVhyXIiaG8TXjiUsi8doXUjj8'

# Set up migration of data to Google Sheets
scopes = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive']

credentials = Credentials.from_service_account_file('book_scrape_oauth.json')
gc = gspread.authorize(credentials)

gauth = GoogleAuth()
drive = GoogleDrive(gauth)

# Open a Google sheet
gs = gc.open_by_key(SHEET_KEY)
worksheet1 = gs.worksheet('Sheet1')

# Download the webpage using requests
website = "https://books.toscrape.com/"
result = requests.get(website)
content = result.text

# Create a file and load contents into it
with open('Bookswebpage.html', 'w') as file:
    file.write(content)

# Use BeautifulSoup to parse and extract info
soup = BeautifulSoup(content, 'lxml')
books = soup.find_all("article", class_="product_pod")

book_title_tags = soup.find_all('h3')


def get_book_titles(doc):
    book_titles = [tags.text for tags in book_title_tags]
    return book_titles


def get_book_price(doc):
    book_price_tags = soup.find_all('p', class_='price_color')
    book_prices = [tags.text.replace('Â', '') for tags in book_price_tags]
    return book_prices


def get_stock_availability(doc):
    book_stock_tags = soup.find_all('p', class_='stock_availability')
    book_stock = [tags.text.strip() for tags in book_stock_tags]
    return book_stock


def get_star_rating(doc):
    star_rating_tags = soup.find_all('p', class_='star-rating')
    star_rating = [tags['class'][1] for tags in star_rating_tags]
    return star_rating


def get_book_url(title_tags):
    book_url = []
    for article in title_tags:
        for link in article.find_all('a', href=True):
            url = link['href']
            links = website + url
            if links not in book_url:
                book_url.append(links)
    return book_url


def get_doc(doc):
    # Checks HTTP request success, returns Exception if failed, returns content if success
    if result.status_code != 200:
        raise Exception('Failed to load page {}'.format(result))
    return content


def scrape_multiple_pages(page_num):
    # Scrapes pages and returns a Pandas dataframe
    url = 'https://books.toscrape.com/catalogue/page-'
    titles, prices, stock_availability, stars, urls = [], [], [], [], []

    for page in range(1, page_num + 1):
        doc = get_doc(url + str(page) + '.html')
        titles.extend(get_book_titles(doc))
        prices.extend(get_book_price(doc))
        stock_availability.extend(get_stock_availability(doc))
        stars.extend(get_star_rating(doc))
        urls.extend(get_book_url(book_title_tags))

    book_dictionary = {
        'Title': titles,
        'Price': prices,
        'Stock Availability': stock_availability,
        'Star Rating': stars,
        'URL': urls
    }

    return pd.DataFrame(book_dictionary)


def convert_to_csv(page_num):
    scrape_csv = scrape_multiple_pages(page_num).to_csv('Books2Scrape.csv', index=False)
    return scrape_csv


def write_csv(path, data):
    with open(path, 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(data)
