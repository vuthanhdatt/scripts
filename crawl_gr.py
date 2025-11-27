import requests
import json
import logging

from bs4 import BeautifulSoup

from goodreads import BASE_URL, HEADERS, ParseBookInfo

logging.basicConfig(format='%(asctime)s - %(process)d - %(thread)d - %(message)s', level=logging.INFO)

def read_json_file(path: str) -> list:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def write_json_file(path: str, data: list) -> None:
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)



def main():
    URL = f"{BASE_URL}/review/list/96340232-vu-dat?shelf=recommendation"

    BOOK_DETAIL_PATH = 'data/goodreads.json'

    all_book_detail = read_json_file(BOOK_DETAIL_PATH)
    crawled_book = [book['detail_link'] for book in all_book_detail]
    
    response = requests.get(URL, headers=HEADERS)

    soup = BeautifulSoup(response.content, 'html.parser')
    books_tag = soup.find('tbody', {'id': 'booksBody'})
    all_book_raw = books_tag.find_all('tr', {'class':'bookalike review'})
    
    for book_tag in all_book_raw:
        parser = ParseBookInfo(book_tag)
        detail_link = parser.detail_link
        if detail_link not in crawled_book:
            logging.info(f'Crawling book detail for {parser.title}')
            all_book_detail.append(parser.to_dict())
        else:
            logging.info(f'Book detail for {parser.title} already crawled, skipping...')

    write_json_file(BOOK_DETAIL_PATH, all_book_detail)


main()
    
    