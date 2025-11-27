import requests
import bs4
import logging
import re

BASE_URL = "https://www.goodreads.com"

logging.basicConfig(format='%(asctime)s - %(process)d - %(thread)d - %(message)s', level=logging.INFO)

RATING_STARS_DICT = {
    "it was amazing": 5,
    "really liked it": 4,
    "liked it": 3,
    "it was ok": 2,
    "did not like it": 1,
    "": None,
}


HEADERS = {
    'DNT': '1',
    'Referer': 'https://www.goodreads.com/',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',
    'device-memory': '8',
    'downlink': '10',
    'dpr': '1.5',
    'ect': '4g',
    'rtt': '150',
    'sec-ch-device-memory': '8',
    'sec-ch-dpr': '1.5',
    'sec-ch-ua': '"Chromium";v="142", "Microsoft Edge";v="142", "Not_A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-ch-ua-platform-version': '"19.0.0"',
    'sec-ch-viewport-width': '1709',
    'viewport-width': '1709',
}

def get_author_name(author_uri: str) -> str | None:
    try:
        r = requests.get(f"{BASE_URL}{author_uri}", headers=HEADERS)
        soup = bs4.BeautifulSoup(r.content, 'html.parser')
        author_name = soup.find('span', {'itemprop': 'name'}).text.strip()
    except:
        logging.warning(f'Cannot get author name for author uri {author_uri}')
        author_name = None
    return author_name

class ParseBookInfo:
    def __init__(self, book_tag: bs4.element.Tag):
        self.book_tag = book_tag 

    @property
    def title(self) -> str | None:
        try:
            title = self.book_tag.find('td', {'class':'field title'}).find('a').text.strip()
        except:
            logging.warning(f'Cannot find title for book tag {self.book_tag}')
            title = None
        return title
    
    @property
    def book_link(self) -> str | None:
        try:
            href = self.book_tag.find('td', {'class':'field title'}).find('a')['href']
            book_link = f"{BASE_URL}{href}"  
        except:
            logging.warning(f'Cannot find title for book tag {self.book_tag}')
            book_link = None
        return book_link
    @property
    def book_cover(self) -> str | None:
        try:
            book_cover = self.book_tag.find('td', {'class':'field cover'}).find('img')['src']
            book_cover = re.sub(r'\._[A-Z0-9]+_\.', '.', book_cover)
        except:
            logging.warning(f'Cannot find book cover for book tag {self.book_tag}')
            book_cover = None
        return book_cover
    
    @property
    def rating(self) -> int | None:
        try:
            rating_text = self.book_tag.find('td', {'class':'field rating'}).find('span', {'class':'staticStars'}).text.strip().lower()
            rating = RATING_STARS_DICT.get(rating_text, None)
        except:
            logging.warning(f'Cannot find rating for book tag {self.book_tag}')
            rating = None
        return rating

    @property
    def author(self) -> str | None:
        try:
            author_uri = self.book_tag.find('td', {'class':'field author'}).find('a')['href']
            author = get_author_name(author_uri)
        except:
            logging.warning(f'Cannot find author for book tag {self.book_tag}')
            author = None
        return author
    
    @property
    def read_date(self) -> str | None:
        try:
            read_date = self.book_tag.find('td', {'class':'field date_read'}).find('div', {'class':'value'}).text.strip()
        except:
            logging.warning(f'Cannot find read date for book tag {self.book_tag}')
            read_date = None
        return read_date
    
    @property
    def detail_link(self) -> str | None:
        try:
            detail_link = self.book_tag.find('td', {'class':'field actions'}).find('a')['href']
            detail_link = f"{BASE_URL}{detail_link}"
        except:
            logging.warning(f'Cannot find detail link for book tag {self.book_tag}')
            detail_link = None
        return detail_link
    
    def to_dict(self) -> dict:
        return {
            'title': self.title,
            'book_link': self.book_link,
            'book_cover': self.book_cover,
            'rating': self.rating,
            'author': self.author,
            'read_date': self.read_date,
            'detail_link': self.detail_link,
        }
