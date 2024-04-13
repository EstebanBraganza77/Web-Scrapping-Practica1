from source import utils
from source import scrapper

def main():
    save_path = './data'
    topics_list =  [
    "Fantasy art",
    "Science fiction art",
    "Anime and manga art",
    "Fan art (for specific fandoms)",
    "Digital paintings",
    "Traditional drawings",
    "Character designs",
    "Creature concepts",
    "Landscape art",
    "Abstract art",
    "Surrealism",
    "Steampunk art",
    "Cyberpunk art",
    "Gothic art",
    "Horror art",
    "Cosplay photography",
    "Pixel art",
    "Concept art",
    "Comics and graphic novels",
    "Street art and graffiti"
]
    data_crawler = scrapper.DeviantArtScraper(max_pages = 30, topics=topics_list, save_path=save_path)
    data_crawler.run_scrapper()
    data_crawler.save_csv()

if __name__ =='__main__':
    main()