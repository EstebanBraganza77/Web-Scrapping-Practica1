import requests
from bs4 import BeautifulSoup


def convert_views(metric_str: str) -> int:
    """
    Converts a string of any metric field to an integer,
    replacing 'K' for thousands or 'M' for millions.
    """
    if "K" in metric_str:
        return int(float(metric_str.replace("K", "")) * 1000)
    elif "M" in metric_str:
        return int(float(metric_str.replace("M", "")) * 1000000)
    return int(metric_str)


def get_info_from_url(url: str) -> dict:
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
        image_favs = convert_views(
            [metric.split(" ")[0] for metric in metrics if "Favourites" in metric][-1]
        )
        image_com = [
            int(metric.split(" ")[0]) for metric in metrics if "Comments" in metric
        ][0]
        image_views = convert_views(
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

        try:
            num_comments = int(soup.find("span", class_="eVBLr").text)
        except AttributeError:
            num_comments = 0

        if num_comments > 0:
            try:
                last_comment = (
                    soup
                    .find("span", class_="_2PHJq")
                    .text
                ).strip()
            except:
                last_comment = ''

        results = {
            "image_url": image_url,
            "image_title": image_title,
            "image_author": image_author,
            "image_favs": image_favs,
            "image_com": image_com,
            "image_views": image_views,
            "private_collections": private_collections,
            "tags": tags,
            "location": location,
            "description": description,
            "image_px": image_px,
            "image_size": image_size_mb,
            "published_date": published_date,
            "num_comments": num_comments,
            "last_comment": last_comment,
        }

    return results
