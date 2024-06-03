from loguru import logger
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests
import time
import numpy as np

class Article:
    id: str = None
    url: str = None
    title: str = None
    tag: str = None
    

def main():
    articles_data = []
    previous_first_article_title
    i = 1
    # TODO: сделать по аналогии с parse_page
    # https://colab.research.google.com/drive/1VXAmkN9VcqQesUE9byNJyQ7l7gjFg4ZM#scrollTo=sV-n6jw9XP0A
    while True:
        time.sleep(np.random.choice([3, 5, 7]))
        
        try:
            response = requests.get(f'https://lenta.ru/parts/news/{i}/', headers={'User-Agent': UserAgent().chrome})
            logger.info(response.text)
        except Exception as error:
            logger.error(error)
            
        tree = BeautifulSoup(response.content)
            
        articles_on_page = tree.find_all('a', {'class' : 'card-full-news _parts-news'})
        articles_on_page_data = []
        
        for article in articles_on_page:
            article_object = Article()
            article_object.title = article.h3.text
            article_object.url = 'https://lenta.ru/' + article.get('href')
            article_object.tag = article.find_all('a', {'class' : 'card-full-news__info-item card-full-news__rubric'})
            date = article.find_all('a', {'class' : 'card-full-news__info-item card-full-news__date'})
            article_object.id = f'{article_object.title}{date}'
            
            articles_on_page_data.append(article_object)
            
        if articles_on_page_data[0].title == previous_first_article_title or i > 10: # 50:
            break
        
        articles_data.extend(articles_on_page_data)
        previous_first_article_title = articles_on_page_data[0].title
        i += 1
    
    
        


if __name__ == '__main__':
    main()