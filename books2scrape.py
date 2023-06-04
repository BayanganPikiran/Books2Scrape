import requests
from bs4 import BeautifulSoup
import time
import csv
import re

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


def get_book_titles(doc):
    book_title_tags = soup.find_all('h3')
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


def get_book_url(book_title_tags):
    book_url = []
    for article in book_title_tags:
        for link in article.find_all('a', href=True):
            url = link['href']
            links = website + url
            if links not in book_url:
                book_url.append(links)
    return book_url
