# Web Scrapping Práctica 1
Contiene la práctica 1 de la materia `Tipología y ciclo de vida de los datos`, segundo semestre, curso 2023-2024.

## Nombres de los integrantes del grupo
Esteban Braganza Cajas y Ana M. Álvarez Sánchez

## Archivos que componen el repositorio

El repositorio está compuesto por los siguientes archivos:
* `requeriments.txt`: incluye el listado de todas las dependencias del proyecto.
* `main.py`: script que permite la ejecución del scraper para obtener el dataset.
* `source`: directorio que contiene el código fuente del programa.
    * `scraper.py`: archivo donde se define la clase `DeviantArtScraper` y sus métodos.
    * `pruebas.ipynb`: notebook con ejemplos de uso del scraper.
* `dataset`: directorio que contiene el csv resultante de la ejecución del scraper.
    * `images_db.csv`: archivo compuesto por más de 6500 registros de imágenes.
* `documents`: directorio que contiene la memoria del ejercicio en pdf.

## Cómo usar el código generado
Parámetros que admite el script y uno o varios ejemplos replicables de su uso.

El scraper de la clase `DeviantArtScraper` toma tres parámetros:
* La lista de `strings` que buscará.
* El número de páginas que recorrerá de cada búsqueda, teniendo en cuenta que cada página incluye 24 imágenes.
* El `path` al directorio donde se guardará el dataset.

Para la ejecución de este scraper se deben seguir los siguientes pasos:

```python
import source.scraper as scraper

num_pages = 10
topics_list = ["horses", "ski", "yellow"]
save_path = "./dataset"

# Crea el objeto de clase DeviantArtScraper
data_crawler = scraper.DeviantArtScraper(
        max_pages=num_pages, topics=topics_list, save_path=save_path
    )

# Ejecuta el método run_scraper()
data_crawler.run_scraper()

# Guarda los resultados como csv
data_crawler.save_csv()

```



## DOI de Zenodo del dataset generado
