# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import re
from collections import OrderedDict
from urllib.parse import urljoin

from scrapy import log
from scrapy.exporters import JsonLinesItemExporter

from imdb_crawler.exceptions import ImdbMovieNotValidException
from imdb_crawler.settings import IMDB_DOMAIN


class ImdbSpiderPipeline(object):
    """
    item = {
        'rate': (str),
        'title': (str),
        'year': (str),
        'url': (str)',
        'genre': (str),
    }
    """

    def process_item(self, item, spider):
        item = self.clean(item)
        if not self.is_valid(item):
            log.msg(f'Item not valid: {item}', level=log.WARNING, spider=spider)
            raise ImdbMovieNotValidException

        exporter = self._exporter_for_genre(item['genre'])
        exporter.export_item(item)
        log.msg(f'Movie exported: {item["title"]}', level=log.INFO, spider=spider)
        return None

    def open_spider(self, spider):
        self.genres_to_exporter = dict()
        return None

    def close_spider(self, spider):
        for exporter in self.genres_to_exporter.values():
            exporter.finish_exporting()
            exporter.file.close()
        return None

    def clean(self, item):
        """
        Clean the fields of item.
        Using a OrderedDict make the output data more readable.

        returns item(OrderedDict) with fields: ('rate', 'title', 'year', 'url', 'genre')
        """
        ordered_item = OrderedDict()
        ordered_item['rate'] = item['rate'].strip()
        ordered_item['title'] = item['title'].strip()
        year_regex = re.search(r'\(.*?(\d+).*?\)', item['year'])
        if year_regex:
            ordered_item['year'] = year_regex.group(1)
        else:
            ordered_item['year'] = None
        ordered_item['url'] = urljoin(IMDB_DOMAIN, item['url'].strip())
        ordered_item['genre'] = item['genre'].lower()
        return ordered_item

    def is_valid(self, item):
        """
        Validates if the 'item' has all fields filled in.
        """
        for value in item.values():
            if not value:
                return False
        return True

    def _exporter_for_genre(self, genre_name):
        if genre_name not in self.genres_to_exporter:
            f = open(f'exported_movies/{genre_name}.jl', 'wb')
            exporter = JsonLinesItemExporter(f)
            exporter.start_exporting()
            self.genres_to_exporter[genre_name] = exporter
        return self.genres_to_exporter[genre_name]
