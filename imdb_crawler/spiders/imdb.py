import re

import scrapy
from urllib.parse import parse_qs, urlparse, urlunparse, urljoin, urlencode

from imdb_crawler.exceptions import ImdbMovieNotValidException
from imdb_crawler.settings import IMDB_DOMAIN


def custom_genre_url(url_path):
    """
    Add querystring to sort the imdb movies by rating.

    Returns (str): url
    """
    parsed_url = urlparse(urljoin(IMDB_DOMAIN, url_path))
    parsed_qs = parse_qs(parsed_url.query)

    parsed_qs['sort'] = ['user_rating,desc']
    parsed_qs['view'] = ['simple']
    new_qs = urlencode(parsed_qs, doseq=True)

    return urlunparse((
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        parsed_url.params,
        new_qs,
        parsed_url.fragment
    ))


class ImdbSpider(scrapy.Spider):
    name = 'imdb_top500_by_genre'
    start_urls = [
        'https://www.imdb.com/feature/genre'
    ]

    movies_per_genre_limit = 500
    movies_per_genre_counter = dict()

    def parse(self, response):
        genre_list = response.xpath('//*[@id="main"]/div[6]/span/div/div//div[@class="table-row"]//a')
        for genre in genre_list:
            genre_name = genre.xpath('text()').extract_first().strip()
            genre_path = genre.xpath('@href').extract_first()

            request = scrapy.Request(custom_genre_url(genre_path), callback=self.parse_movies)
            request.meta['genre_name'] = genre_name
            yield request

    def parse_movies(self, response):
        """
        Parse the movies data.
        Some contracts are mingled with this docstring.

        @url https://www.imdb.com/search/title?genres=action&title_type=feature&explore=genres&pf_rd_m=A2FGELUUNOQJNL&pf_rd_p=17d3863a-3e07-4c9b-a09a-f643edc8e914&pf_rd_r=Z2JRBJZWJ7YKDSF42FCB&pf_rd_s=center-6&pf_rd_t=15051&pf_rd_i=genre&view=simple&sort=user_rating,desc&ref_=ft_gnr_mvpop_1
        @scrapes genre url title year rate
        """
        movies = response.css('div.lister-list div.lister-item-content')

        if response.meta.get('genre_name'):
            genre_name = response.meta['genre_name']
        else:
            page_title = response.xpath(
                '//*[@id="main"]/div/h1/text()'
            ).extract_first().strip().replace('"', '')
            genre_regex = re.search(r'Highest Rated (.*) Feature Films', page_title)
            if genre_regex:
                genre_name = genre_regex.group(1).lower()
            else:
                raise ImdbMovieNotValidException

        if self.movies_per_genre_counter.get(genre_name, None) is None:
            self.movies_per_genre_counter[genre_name] = 0

        for movie in movies:
            if self.movies_per_genre_counter[genre_name] >= self.movies_per_genre_limit:
                return None
            self.movies_per_genre_counter[genre_name] += 1

            yield {
                'genre': genre_name,
                'url': movie.css('span[title] a::attr(href)').extract_first(),
                'title': movie.css('span[title] a::text').extract_first(),
                'year': movie.css('span.lister-item-year::text').extract_first(),
                'rate': movie.css('div.col-imdb-rating strong::text').extract_first(),
            }

        next_page = response.css('a.next-page::attr(href)').extract_first()
        if next_page is not None:
            request = response.follow(next_page, callback=self.parse_movies)
            request.meta['genre_name'] = genre_name
            yield request
