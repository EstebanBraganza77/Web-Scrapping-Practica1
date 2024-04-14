import json
import os
import time
import urllib.parse
from typing import Any, Dict, List

import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By


class DeviantArtScraper:
    def __init__(self, max_pages: int, topics: List[str], save_path: str) -> None:
        """
        Initializes a DeviantArtScraper object.

        Args:
            max_pages (int): The maximum number of pages to scrape for each topic.
            topics (list): A list of topics to search for on DeviantArt.
            save_path (str): The path where the scraped data will be saved.

        Attributes:
            max_pages (int): The maximum number of pages to scrape for each topic.
            topics (list): A list of topics to search for on DeviantArt.
            base_url (str): The base URL for the DeviantArt search page.
            save_path (str): The path where the scraped data will be saved.
            information (dict): A dictionary to store the scraped information.
            error_links (list): A list to store any error links encountered during scraping.

        Returns:
            None
        """
        self.max_pages = max_pages
        self.topics = topics
        self.base_url = "https://www.deviantart.com/search"
        self.save_path = save_path
        self.information = {"data": [], "search_topic": [], "page_num": []}
        self.error_links = []
        self.start_driver()

    def close_driver(self) -> None:
        self.driver.close()

    def start_driver(self) -> None:
        self.driver = webdriver.Chrome()

    def run_scraper(self) -> None:
        """
        Method responsible for running the scraper.
        """
        # Iterates over each topic and performs the scraping process for each page
        for topic in self.topics:
            parsed_topic = urllib.parse.quote(topic)
            search_url = f"{self.base_url}?q={parsed_topic}"
            page = 0
            while page < self.max_pages:
                print(f"Entering page {page}")
                self.driver.get(search_url)
                time.sleep(3)

                # Get links to every image
                image_classes = self.driver.find_elements(By.CLASS_NAME, "_3Y0hT")
                image_links = [
                    image.find_element(By.TAG_NAME, "a").get_attribute("href")
                    for image in image_classes
                ]
                self.navigate_images_links(
                    image_links=image_links, page=page, topic=topic
                )

                # Go to next page
                try:
                    next_page = self.driver.find_element(By.LINK_TEXT, "Next")
                    search_url = next_page.get_attribute("href")
                except Exception as e:
                    print(f"Error finding a new page {topic}, page: {page}")
                    print(e)
                    break
                page += 1

        # Close browser
        self.close_driver()

        # Generate dataframe
        self.generate_df()

    def navigate_images_links(
        self, image_links: List[str], page: int, topic: str
    ) -> None:
        """
        Navigate through a list of image links and extract information from each link.

        If there is an error while processing a link, the error is printed and the link is added to the error_links list.

        Args:
            image_links: A list of image links to navigate through.
            page: The page number associated with the image links.
            topic: The topic associated with the image links.
        """
        for link in image_links:
            time.sleep(2)
            try:
                self.information["data"].append(self.get_info_from_url(link))
                self.information["search_topic"].append(topic)
                self.information["page_num"].append(page)
            except Exception as e:
                print(
                    f"There was an error trying to process the following link: {link}, page {page}, topic {topic}"
                )
                print(e)
                self.error_links.append(link)

    def generate_df(self) -> None:
        """
        Generates a pandas DataFrame from the scraped information stored in the 'information' attribute.
        """
        self.df = pd.DataFrame(self.information)
        self.df = pd.concat(
            [
                self.df.loc[:, ["search_topic", "page_num"]],
                pd.json_normalize(self.df["data"]),
            ],
            axis=1,
        )

    def save_csv(self) -> None:
        """
        Saves the scraped information in CSV format.
        """
        self.df.to_csv(f"{self.save_path}/images_db.csv", index=False)

    def save_json(self):
        """
        Saves the scraped information in JSON format.
        """
        with open(f"{self.save_path}/images_db.json", "w") as json_file:
            json.dump(self.information, json_file)

    def convert_views(self, metric_str: str) -> int:
        """
        Converts a string of any metric field to an integer.

        Replaces 'K' for thousands or 'M' for millions.
        """
        if "K" in metric_str:
            return int(float(metric_str.replace("K", "")) * 1000)
        elif "M" in metric_str:
            return int(float(metric_str.replace("M", "")) * 1000000)
        return int(metric_str)

    def get_info_from_url(self, url: str) -> Dict[str, Any]:
        """
        Get information from a given URL.

        Args:
            url: The URL of the webpage from which information needs to be extracted.

        Returns:
            A dictionary containing the extracted information from the webpage.
        """
        with requests.Session() as session:
            try:
                page = session.get(url, timeout=5)
            except requests.exceptions.RequestException as e:
                print(f"An error occurred during the request: {e}")
                raise e

            if page is None or page.status_code != 200:
                # Handle cases where the page is not retrieved successfully
                print("Failed to get page")
                raise ValueError

            soup = BeautifulSoup(page.text, "html.parser")

            # Main image fields
            image_page = url
            image_url = soup.find("div", class_="_2SlAD").find("img")["src"]
            image_title = soup.find("div", class_="U2aSH").text
            image_author = soup.find("span", class_="_12F3u").text

            # Image metrics (favs, comments, views and private collections)
            metrics = [metric.text for metric in soup.find_all("span", class_="_3AClx")]

            # In some cases "metrics" returns several values for favorites, the correct one will be the last one
            image_favs = self.convert_views(
                [
                    metric.split(" ")[0]
                    for metric in metrics
                    if "Favourites" in metric or "Favourite" in metric
                ][-1]
            )
            num_comments = [
                int(metric.split(" ")[0])
                for metric in metrics
                if "Comments" in metric or "Comment" in metric
            ][0]
            image_views = self.convert_views(
                [
                    metric.split(" ")[0]
                    for metric in metrics
                    if "Views" in metric or "View" in metric
                ][0]
            )

            try:
                private_collections = [
                    int(metric.split(" ")[0])
                    for metric in metrics
                    if "Collected Privately" in metric
                ][0]
            # If this field does not exist in metrics, it returns 0
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

            try:
                image_px = soup.find("div", class_="_3RVC5").next_sibling.text.split(
                    "px"
                )[0]
            except AttributeError:
                image_px = None

            try:
                image_size_mb = float(
                    soup.find("div", class_="_3RVC5")
                    .next_sibling.text.split("px")[1]
                    .strip()
                    .split(" ")[0]
                )
            except AttributeError:
                image_size_mb = None

            published_date = soup.find("div", class_="_1mcmq").find("time")["datetime"]

            if num_comments > 0:
                try:
                    last_comment = (soup.find("span", class_="_2PHJq").text).strip()
                except AttributeError:
                    last_comment = None
            else:
                last_comment = None

            try:
                image_license = soup.find("div", class_="_2GljG").text
            except AttributeError:
                image_license = None

            results = {
                "image_page": url,
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
                "image_license": image_license,
            }

        return results

    def download_image(
        self, url_image: str, images_folder: str = "./deviantart_images"
    ) -> None:
        """
        Downloads an image from a given URL.
        """
        # Create the directory if it does not exist
        if not os.path.exists(images_folder):
            os.makedirs(images_folder)

        # Extract image name from url
        image_title = url_image.split("?")[0].split("/")[-1]

        response = requests.get(url_image, stream=True)
        if response.status_code == 200:
            with open(f"{images_folder}/{image_title}", "wb") as out_file:
                out_file.write(response.content)
        else:
            print(f"Error downloading image: {url_image}")
