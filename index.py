from loguru import logger
from bs4 import BeautifulSoup
import requests

def main():
    # задержка
    # user agent   

    i = 1
    while True:
        
        
        
        try:
            response = requests.get(f'https://lenta.ru/parts/news/{i}/')
            
            tree = BeautifulSoup(response.content)
            
            articles = tree.find_all('a', {'class' : 'card-full-news _parts-news'})
            
            for article in articles:
                title = article.h3.text
                url = 'https://lenta.ru/' + article.get('href')
            
            logger.info(response.text)
        except Exception as error:
            logger.error(error)
            
        if current_first_article_title == previous_first_article_title or i > 50:
            break
        
        previous_first_article_title = current_first_article_title
        i += 1
    
    
        


if __name__ == '__main__':
    main()