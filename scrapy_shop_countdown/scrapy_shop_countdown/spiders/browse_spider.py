# -*- coding: utf-8 -*-
import json
import time

import scrapy
from scrapy import cmdline, Request

from scrapy_shop_countdown.items import BrowseItem


class BrowseSpider(scrapy.Spider):
    name = 'browse_spider'
    allowed_domains = ['shop.countdown.co.nz']
    browses_url = "https://shop.countdown.co.nz/api/v1/shell"
    browse_list_url = "https://shop.countdown.co.nz/api/v1/products?dasFilter=Department%3B%3B{browse_url}%3Bfalse&target=browse&page={page}&size=120"
    browse_item_url = "https://shop.countdown.co.nz/api/v1/products/{sku}"
    date = time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(time.time()))
    browse_file_name = date + "_browse.json"

    def start_requests(self):
        self.log_file = open("browse_log.txt", "a+")
        # 请求browse的各个种类
        yield Request(url=self.browses_url,
                      callback=self.parse_browses,
                      meta={
                      },
                      dont_filter=True)

    def parse_browses(self, response):
        if response.status == 200:
            try:
                content = response.text
                content = json.loads(content)
                # 获取browse列表
                browses = content.get('browse')
                # 遍历browse列表，构建链接
                for browse in browses:
                    try:
                        browse_url = browse.get('url')
                        browse_list_url = self.browse_list_url.format(browse_url=browse_url, page=1)
                        yield Request(url=browse_list_url,
                                      callback=self.parse_browse_list,
                                      meta={
                                          'browse_url': browse_url,
                                          'page': 1
                                      },
                                      dont_filter=True)
                    except Exception as e:
                        print("Traversal browses Error",e)
            except Exception as e:
                print("Parse_browses Error:", e)

    def parse_browse_list(self, response):
        current_browse_url = response.meta['browse_url']
        current_page = response.meta['page']
        if response.status == 200:
            try:
                content = response.text
                content = json.loads(content)
                # 获取products字段
                products = content.get('products')
                # 获取该类的总数
                totalItems = products.get('totalItems')
                # 获取items列表
                items = products.get('items')
                for item in items:
                    try:
                        # 获取sku字段构建详细信息链接
                        sku = item.get('sku')
                        browse_item_url = self.browse_item_url.format(sku=sku)
                        yield Request(url=browse_item_url,
                                      callback=self.parse_browse_item,
                                      dont_filter=True)
                    except Exception as e:
                        print("Traversal products_items Error", e)
                # 如果当前页数乘以120少于总数，说明有下一页（每页有120个项目）
                if current_page*120 < totalItems:
                    browse_list_url = self.browse_list_url.format(browse_url=current_browse_url, page=current_page+1)
                    yield Request(url=browse_list_url,
                                  callback=self.parse_browse_list,
                                  meta={
                                      'browse_url': current_browse_url,
                                      'page': current_page+1
                                  },
                                  dont_filter=True)
                else:
                    self.log_file.write("{kind}类别已爬取完，一共爬取{page}页\n".format(kind=current_browse_url, page=current_page))
            except Exception as e:
                print("Parse_browse_list Error:", e)
        else:
            self.log_file.write("链接:{url},状态:{status}\n".format(url=response.url, status=response.status))

    def parse_browse_item(self, response):
        if response.status == 200:
            try:
                content = response.text
                item = BrowseItem()
                item['content'] = content
                item['file_name'] = self.browse_file_name
                yield item
            except Exception as e:
                print("Parse_browse_item Error:", e)
        else:
            self.log_file.write("链接:{url},状态:{status}\n".format(url=response.url, status=response.status))


if __name__ == '__main__':
    cmdline.execute("scrapy crawl browse_spider".split())