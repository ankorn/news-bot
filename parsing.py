from loguru import logger
import re
import time
import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup
from selenium import webdriver
from dataclasses import dataclass
from io import StringIO
from html.parser import HTMLParser
from constants import DEPTH, BASE_URL, TOPICS, DEPTH, SLEEP

@dataclass
class Article:
    id: str = None
    url: str = None
    title: str = None
    subtitle: str = None
    text: str = None
    datetime: str = None
    topic: str = None

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

def strip_html(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data().replace('\xa0', ' ').replace('\n', ' ')

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('headless')
chrome_options.add_argument('no-sandbox')
chrome_options.add_argument('disable-dev-shm-usage')
driver = webdriver.Chrome(options=chrome_options)

def parse_article(article_card_soup, topic):
    article = Article()

    article.url = article_card_soup['href']

    article.topic = topic

    s = re.findall(r'\d+.shtml', article.url)[0]
    article.id = s[ : s.find('.')]

    driver.get(BASE_URL + article.url)
    time.sleep(SLEEP)

    article_page_soup = BeautifulSoup(driver.page_source, "html.parser")
    article_soup = article_page_soup.find_all('article', {'class' : 'b_article', 'itemtype': 'http://schema.org/NewsArticle'})[0]
    text_soup = article_soup.find('div', {'class' : 'b_article-text', 'itemprop': 'articleBody'})
    text_parts_soup = text_soup.find_all('p')

    article.text = ''
    for text_part in text_parts_soup:
        article.text += strip_html(text_part.get_text())

    article.title = strip_html(article_soup.find('h2', {'class' : 'headline', 'itemprop': 'alternativeHeadline'}).get_text())
    article.subtitle = strip_html(article_soup.find('h1', {'class' : 'subheader', 'itemprop': 'headline'}).get_text())
    article.datetime = strip_html(article_soup.find('time', {'class' : 'time', 'itemprop': 'datePublished'}).get_text())

    return article

def parse_articles(news_cards_soup, topic):
    articles = []

    for card in tqdm(news_cards_soup):
        try:
            article = parse_article(card, topic)
            articles.append(article)
        except Exception as error:
            logger.error(error)
            pass
    return articles

def get_articles():
    articles = []

    for topic in tqdm(TOPICS):
        try:
            url = f'{BASE_URL}{topic}/news/'
            current_news_cards_soup = []

            # 30 news per page
            for i in tqdm(range(DEPTH), leave=False):
                try:
                    driver.get(url)
                    time.sleep(SLEEP)

                    soup = BeautifulSoup(driver.page_source, "html.parser")
                    current_news_cards_soup.extend(soup.find_all('a', { 'class': 'b_ear m_techlisting' }))

                    href = soup.find('a', { 'class': 'b_showmorebtn-link' })['href']
                    url = f'{BASE_URL}{href}'
                    
                except Exception as error:
                    logger.error(error)
                    pass

            current_articles = parse_articles(current_news_cards_soup, topic)
            logger.info(f'{topic} articles saved: {len(current_articles)}')
            df = pd.DataFrame(data=current_articles)
            df.to_pickle(f'df_gazeta_{topic}.p', compression='gzip')

            articles.extend(current_articles)

        except Exception as error:
            logger.error(error)
            pass

    return articles

articles = get_articles()

driver.close()

df = pd.DataFrame(data=articles)
df.to_pickle('df_gazeta.p', compression='gzip')