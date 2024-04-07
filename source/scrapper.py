import json
import time
import urllib.parse
import pandas as pd
from utils import *
from selenium import webdriver
from selenium.webdriver.common.by import By

class DeviantArtScraper: 
    def __init__(self, max_pages, topics):
        self.max_pages=max_pages
        self.topics=topics
        self.base_url="https://www.deviantart.com/search"
        self.save_path_csv = './csv_data/images_db.csv'
        self.save_path_json = './json_data/images_db.csv'
        self.information= {
            'data':[],
            'search_topic':[],
            'page_num':[]
        }
        self.error_links = []
        self.start_driver()

    def close_driver(self):
        self.driver.close()

    def start_driver(self):
        self.driver=webdriver.Chrome()

    def run_scrapper(self):
        for topic in self.topics:
            parsed_topic = urllib.parse.quote(topic)
            search_url = f'{self.base_url}?q={parsed_topic}'
            page = 0
            while page < self.max_pages:
                self.driver.get(search_url)
                time.sleep(2)
                # Obtenemos links de cada imagen
                image_classes = self.driver.find_elements(By.CLASS_NAME, "_3Y0hT")
                image_links = [image.find_element(By.TAG_NAME, 'a').get_attribute('href') for image in image_classes]
                for link in image_links:
                    try:
                        self.information['data'].append(get_info_from_url(link))
                        self.information['search_topic'].append(topic)
                        self.information['page_num'].append(page)
                    except Exception as e:
                        print(f' Ha habido un error al tratar de procesar el siguiente link: {link}, pagina {page}, tema {topic}')
                        print(e)
                        self.error_links.append(link)
                # Navegamos a la siguiente pagina.
                try:
                    next_page = self.driver.find_element(By.LINK_TEXT,'Next')
                    search_url = next_page.get_attribute('href')
                except Exception as e:
                    print(f'Error al encontrar una nueva pagina {topic}, page: {page}')
                    print(e)
                    break
                page += 1
        # Ceerramos el browser
        self.close_driver()

    def generate_df(self):
        self.df = pd.DataFrame(self.information)
        self.df = pd.concat([self.df.loc[:,['search_topic', 'page_num']], pd.json_normalize(self.df['data'])], axis=1)
        
    def save_csv(self):
        self.df.to_csv(self.save_path, sep=',')

    def save_json(self):
        with open(self.save_path_json, 'w') as json_file:
            json.dump(self.information, json_file)