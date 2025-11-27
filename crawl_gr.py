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
    URL = f"{BASE_URL}/review/list/96340232-vu-dat?order=d&shelf=recommendation&sort=date_read"

    BOOK_DETAIL_PATH = 'data/goodreads.json'

    all_book_detail = read_json_file(BOOK_DETAIL_PATH)
    
    response = requests.get(URL, headers=HEADERS)

    soup = BeautifulSoup(response.content, 'html.parser')
    books_tag = soup.find('tbody', {'id': 'booksBody'})
    all_book_raw = books_tag.find_all('tr', {'class':'bookalike review'})

    current_shelf_links = set()
    parsers = []

    for book_tag in all_book_raw:
        parser = ParseBookInfo(book_tag)
        parsers.append(parser)
        if parser.detail_link:
            current_shelf_links.add(parser.detail_link)
    
    # Filter out books that are no longer on the shelf
    all_book_detail = [book for book in all_book_detail if book.get('detail_link') in current_shelf_links]
    crawled_book_links = {book['detail_link'] for book in all_book_detail}

    for parser in parsers:
        detail_link = parser.detail_link
        if detail_link not in crawled_book_links:
            logging.info(f'Crawling book detail for {parser.title}')
            all_book_detail.append(parser.to_dict())
        else:
            logging.info(f'Book detail for {parser.title} already crawled, skipping...')

    write_json_file(BOOK_DETAIL_PATH, all_book_detail)


main()
    
    