# Imdb top500
Crawl the top 500 movies of each genre at IMDB.


## Overview
The project was created on top of Scrapy.
Scrapy is a fast high-level web crawling and web scraping framework, used to crawl websites and extract structured data 
from their pages. It can be used for a wide range of purposes, from data mining to monitoring and automated testing.
For more information including a list of features check the Scrapy homepage at: https://scrapy.org


### Requirements
* Python >= 3.5


### Installation and Configuration
> Remember to create a new virtualenv!

```bash
$ git clone git@github.com:marcosflp/imdb_top500.git
$ cd imdb_top500
$ pip install -r requirements.txt
```


## Running the Spider
After running the spider it may take a few minutes for it to 
fetch all the movies.

This command must be run from the project root folder
```bash
$ scrapy crawl imdb_top500_by_genre
```


## Crawled movies
You can find the movies on `<project_root>/exported_movies/` folder.
Each movie is in its genre file.
