# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BrowseItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    file_name = scrapy.Field()
    content = scrapy.Field()

class Specialstem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    file_name = scrapy.Field()
    content = scrapy.Field()

class RecipesItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    file_name = scrapy.Field()
    ingredients = scrapy.Field()
    methods = scrapy.Field()
    url = scrapy.Field()
