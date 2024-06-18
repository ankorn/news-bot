from loguru import logger
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from html.parser import HTMLParser
from io import StringIO
import requests
import time
import numpy as np
import pandas as pd


class Article:
    id: str = None
    url: str = None
    title: str = None
    tag: str = None
    text: str = None


class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def fetch(url):
    time.sleep(np.random.choice([1, 2, 3]))

    try:
        response = requests.get(
            url, headers={'User-Agent': UserAgent().chrome})
        logger.info(url)
    except Exception as error:
        logger.error(error)

    return response


def parse_article(article_card_tree, tag, date):
    article = Article()
    article.title = article_card_tree.h3.text
    article.url = 'https://lenta.ru' + article_card_tree.get('href')
    article.tag = tag
    article.id = f'{article.title}{date}'

    response = fetch(article.url)
    article_tree = BeautifulSoup(response.content, features="html.parser")

    text_parts = article_tree.find_all(
        'p', {'class': 'topic-body__content-text'})
    article.text = ''

    for text_part in text_parts:
        if not text_part:
            logger.warning(f'can\'t find text part for article {article.title}/')
            continue
        article.text += strip_tags(text_part.get_text())

    return article


def parse_article_list(index):
    response = fetch(f'https://lenta.ru/parts/news/{index}/')

    tree = BeautifulSoup(response.content, features="html.parser")

    articles_on_page = tree.find_all(
        'a', {'class': 'card-full-news _parts-news'})

    articles_on_page_data = []
    for article in articles_on_page:
        tagEl = article.find(
            'span', {'class': 'card-full-news__info-item card-full-news__rubric'})
        dateEl = article.find(
            'time', {'class': 'card-full-news__info-item card-full-news__date'})
        
        if not tagEl or not dateEl:
            logger.warning(f'can\'t find tag element or date element of card on page /parts/news/{index}/')
            continue
        
        tag = tagEl.get_text()
        date = dateEl.get_text()
        articles_on_page_data.append(parse_article(article, tag, date))

    return articles_on_page_data


def main():
    # TODO: писать в файл
    articles_data = []
    previous_first_article_title = ''
    i = 1
    while True:
        articles_on_page_data = parse_article_list(i)

        logger.info(articles_on_page_data[0].title)

        # 50:
        if articles_on_page_data[0].title == previous_first_article_title or i > 0:
            break

        articles_data.extend(articles_on_page_data)
        
        previous_first_article_title = articles_on_page_data[0].title
        i += 1
        
    df = pd.DataFrame(data=articles_data)
    df.to_pickle('df_final.p', compression='gzip')


if __name__ == '__main__':
    main()
