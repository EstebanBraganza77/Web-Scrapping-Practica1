import json
import time
import requests
from bs4 import BeautifulSoup
import urllib.parse
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By

class DeviantArtScraper: 
    def __init__(self, max_pages: int, topics: list, save_path: str):
        self.max_pages=max_pages
        self.topics=topics
        self.base_url="https://www.deviantart.com/search"
        self.save_path_csv = save_path + '/images_db.csv'
        self.save_path_json = save_path + '/images_db.json'
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
                        self.information['data'].append(self.get_info_from_url(link))
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
        self.generate_df()
        self.df.to_csv(self.save_path_csv, sep=',')

    def save_json(self):
        with open(self.save_path_json, 'w') as json_file:
            json.dump(self.information, json_file)

    def convert_views(self, metric_str: str) -> int:
        """
        Converts a string of any metric field to an integer,
        replacing 'K' for thousands or 'M' for millions.
        """
        if "K" in metric_str:
            return int(float(metric_str.replace("K", "")) * 1000)
        elif "M" in metric_str:
            return int(float(metric_str.replace("M", "")) * 1000000)
        return int(metric_str)

    def get_info_from_url(self, url: str) -> dict:
        """
        Get information from a given URL.

        Args:
            url (str): The URL of the webpage from which information needs to be extracted.

        Returns:
            dict: A dictionary containing the extracted information from the webpage.
        """
        with requests.Session() as session:
            try:
                page = session.get(url, timeout=5)
            except requests.exceptions.RequestException as e:
                print(f"An error occurred during the request: {e}")
                return None

            if page is None or page.status_code != 200:
                # Handle cases where the page is not retrieved successfully
                print("Failed to get page")
                return None

            soup = BeautifulSoup(page.text, "html.parser")

            # Campos principales de la imagen
            image_url = soup.find("div", class_="_2SlAD").find("img")["src"]
            image_title = soup.find("div", class_="U2aSH").text
            image_author = soup.find("span", class_="_12F3u").text

            # Métricas de la imagen (favs, comments, views y private_collections)
            metrics = [metric.text for metric in soup.find_all("span", class_="_3AClx")]

            # En algunos casos metrics devuelve varios valores para favoritos, el correcto será el último
            image_favs = self.convert_views(
                [metric.split(" ")[0] for metric in metrics if "Favourites" in metric][-1]
            )
            num_comments = [
                int(metric.split(" ")[0]) for metric in metrics if "Comments" in metric
            ][0]
            image_views = self.convert_views(
                [metric.split(" ")[0] for metric in metrics if "Views" in metric][0]
            )

            try:
                private_collections = [
                    int(metric.split(" ")[0])
                    for metric in metrics
                    if "Collected Privately" in metric
                ][0]
            # Si no existe este campo en metrics devuelve 0
            except IndexError:
                private_collections = 0

            tags = [tag.text for tag in soup.find_all("span", class_="_1nwad")]

            try:
                description = (
                    soup.find(
                        "div", class_="legacy-journal _2DahR _3bG54 maturefilter _3if5g"
                    )
                    .get_text(separator=" ", strip=True)
                    .replace("\xa0", "\n")
                )
            except AttributeError:
                description = None

            try:
                location = soup.find("div", class_="_3FMM3").text.split("\xa0")[-1]
            except AttributeError:
                location = None

            image_px = soup.find("div", class_="_3RVC5").next_sibling.text.split("px")[0]
            image_size_mb = float(
                soup.find("div", class_="_3RVC5")
                .next_sibling.text.split("px")[1]
                .strip()
                .split(" ")[0]
            )

            published_date = soup.find("div", class_="_1mcmq").find("time")["datetime"]

            if num_comments > 0:
                try:
                    last_comment = (soup.find("span", class_="_2PHJq").text).strip()
                except:
                    last_comment = ""

            results = {
                "image_url": image_url,
                "image_title": image_title,
                "image_author": image_author,
                "image_favs": image_favs,
                "image_com": num_comments,
                "image_views": image_views,
                "private_collections": private_collections,
                "tags": tags,
                "location": location,
                "description": description,
                "image_px": image_px,
                "image_size": image_size_mb,
                "published_date": published_date,
                "last_comment": last_comment,
            }

        return results