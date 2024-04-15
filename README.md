# Web Scraping Práctica 1
Contiene la práctica 1 de la materia `Tipología y ciclo de vida de los datos`, segundo semestre, curso 2023-2024.

## Nombres de los integrantes del grupo
Esteban Braganza Cajas y Ana Álvarez Sánchez

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
* `topics`: la lista de `strings` que buscará.
* `max_pages`: El número de páginas que recorrerá de cada búsqueda, teniendo en cuenta que cada página incluye 24 imágenes.
* `save_path`: El `path` al directorio donde se guardará el dataset.

Se puede ejecutar el script `main.py` y obtener el dataset que se encuentra en ``dataset/images_db.csv`. Para hacerlo, desde el directorio de este repositorio:

```bash
# Instalamos dependencias
pip install -r requeriments.txt

# Ejecutamos script
python3 main.py
```


También podemos ejecutar el scraper usando python desde la ubicación de este directorio y eligiendo cada uno de estos parámetros, de la siguiente forma:

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

# Explora dataframe generado
data_crawler.df

# Guarda los resultados como csv
data_crawler.save_csv()

# Guarda los resultados como json
data_crawler.save_json()

```

Y del dataframe obtenido se pueden descargar las imágenes localmente:

```python
import pandas as pd

df_images = data_crawler.df

first_image_url = df_images.loc[0, "image_url"]

data_crawler.download_image(first_image_url)

```
## Descripción del dataset

El dataset está compuesto por los siguientes campos:
* `search_topic`: la imagen es resultado de la búsqueda por este tema
* `page_num`: la imagen aparece en este número de página de la búsqueda
* `image_page`: enlace a la página con la información de la imagen
* `image_url`: enlace a la imagen
* `image_title`: título de la imagen
* `image_author`: autor/a de la imagen
* `image_favs`: número de veces que le han dado a “me gusta” en la imagen
* `image_com`: número de comentarios que tiene la imagen
* `image_views`: número de vistas a la imagen
* `private_collections`: número de veces que ha sido incluida en una colección privada
* `tags`: etiquetas que se le han asignado a la imagen para facilitar su descubrimiento
* `location`: país o localización geográfica, si el autor la quiere identificar
description: campo de texto abierto creado por el autor, que acompaña a la imagen. Puede incluir detalles técnicos o enlaces a las redes sociales del autor/a.
* `image_px`: dimensiones de la imagen, en pixeles
* `image_size`: peso de la imagen en MB.
* `published_date`: fecha de publicación de la imagen.
* `last_comment`: último comentario añadido a la imagen.
* `license`: licencia de la imagen

## DOI de Zenodo del dataset generado

DOI: https://doi.org/10.5281/zenodo.10974440 