# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import csv
import time

from scrapy_shop_countdown.items import BrowseItem, Specialstem


class ScrapyShopCountdownPipeline(object):
    def __init__(self):
        self.recipes_file = None
        self.browse_file = None
        self.specials_file = None

    def process_item(self, item, spider):
        if isinstance(item,BrowseItem):
            self.browse_file = open(item['file_name'], "a+", encoding="utf-8")
            self.browse_file.write(item['content']+"\n")
        elif isinstance(item,Specialstem):
            self.specials_file = open(item['file_name'], "a+", encoding="utf-8")
            self.specials_file.write(item['content']+"\n")
        else:
            self.recipes_file = open(item['file_name'],"a+",encoding="utf-8",newline='')
            writer = csv.writer(self.recipes_file)
            writer.writerow([item['ingredients'],item['methods'],item['url']])
        return item

    def close_spider(self, spider):
        if self.browse_file != None:
            self.browse_file.close()
        if self.specials_file != None:
            self.specials_file.close()
        if self.recipes_file != None:
            self.recipes_file.close()
