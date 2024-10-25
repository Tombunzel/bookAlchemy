import os
import json
import requests
from dotenv import load_dotenv
import wikipedia

load_dotenv()
API_KEY = os.environ.get('API_KEY')
API_URL = 'https://www.googleapis.com/books/v1/volumes?q='
WIKI_REQUEST = ('http://en.wikipedia.org/w/api.php?'
                'action=query&prop=pageimages'
                '&format=json&piprop=original&titles=')


def add_book_info(books):
    """
    fetches from Google's books api a thumbnail, book description, and publisher
    returns a list of book dicts
    """
    books_for_html = []
    for book in books:
        book_for_html = {'title': book.title,
                         'author': book.author.name,
                         'author_id': book.author.id,
                         'isbn': book.isbn,
                         'year': book.publication_year,
                         'id': book.id}
        api_url = API_URL + f'isbn:{book.isbn}&key={API_KEY}'
        res = requests.request('GET', api_url).json()
        try:
            thumbnail_url = res['items'][0]['volumeInfo']['imageLinks']['thumbnail']
            big_thumbnail_url = thumbnail_url.replace('zoom=1', 'zoom=0')
        except KeyError:
            big_thumbnail_url = None
        try:
            description = res['items'][0]['volumeInfo']['description']
        except KeyError:
            description = None
        try:
            publisher = res['items'][0]['volumeInfo']['publisher']
        except KeyError:
            publisher = None

        book_for_html['description'] = description
        book_for_html['publisher'] = publisher
        book_for_html['thumbnail'] = big_thumbnail_url
        books_for_html.append(book_for_html)

    return books_for_html


def get_author_pic_and_summary(author_name):
    """
    fetches from wikipedia an image of an author
    and a summary of the article about them
    """
    try:
        result = wikipedia.search(author_name, results=1)
        wikipedia.set_lang('en')
        wkpage = wikipedia.WikipediaPage(title=result[0])
        title = wkpage.title
        response = requests.get(WIKI_REQUEST + title)
        json_data = json.loads(response.text)
        img_link = list(json_data['query']['pages'].values())[0]['original']['source']
    except:
        img_link = ""
    try:
        summary = wikipedia.summary(title, auto_suggest=False)
    except:
        summary = ""

    return img_link, summary
