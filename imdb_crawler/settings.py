# -*- coding: utf-8 -*-

# Scrapy settings for imdb_crawler project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'imdb_crawler'

SPIDER_MODULES = ['imdb_crawler.spiders']
NEWSPIDER_MODULE = 'imdb_crawler.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

IMDB_DOMAIN = 'https://www.imdb.com'

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'imdb_crawler.pipelines.ImdbSpiderPipeline': 300,
}


# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 32
