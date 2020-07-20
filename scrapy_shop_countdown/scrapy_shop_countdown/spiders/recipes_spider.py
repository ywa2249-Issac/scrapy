# -*- coding: utf-8 -*-
import csv
import json
import time

import scrapy
from bs4 import BeautifulSoup
from pyquery import PyQuery as pq
from scrapy import Request, cmdline

from scrapy_shop_countdown.items import RecipesItem


class RecipesSpider(scrapy.Spider):
    name = 'recipes_spider'
    allowed_domains = ['shop.countdown.co.nz']
    recipes_url = "https://shop.countdown.co.nz/api/v1/shell"
    recipes_list_url = "https://shop.countdown.co.nz/shop/recipecategory/{recipe_id}?name={recipe_url}&page={page}"
    date = time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(time.time()))
    recipes_file_name = date + "_recipes.csv"

    def start_requests(self):
        # 写csv的表头
        self.log_file = open("recipes_log.txt", "a+")
        recipes_file = open(self.recipes_file_name, "a+", encoding="utf-8", newline='')
        writer = csv.writer(recipes_file)
        writer.writerow(["ingredients", "methods", 'url'])
        # 请求browse的各个种类
        yield Request(url=self.recipes_url,
                      callback=self.parse_recipes,
                      meta={
                      },
                      dont_filter=True)

    def parse_recipes(self, response):
        if response.status == 200:
            try:
                content = response.text
                content = json.loads(content)
                # 获取browse列表
                recipes = content.get('recipes')
                # 遍历browse列表，构建链接
                for recipe in recipes:
                    try:
                        recipe_id = recipe.get('id')
                        recipe_url = recipe.get('url')
                        recipes_list_url = self.recipes_list_url.format(recipe_id=recipe_id, recipe_url=recipe_url,
                                                                        page=1)
                        yield Request(url=recipes_list_url,
                                      callback=self.parse_recipes_list,
                                      meta={
                                          'recipe_id': recipe_id,
                                          'recipe_url': recipe_url,
                                          'page': 1
                                      },
                                      dont_filter=True)
                    except Exception as e:
                        print("Traversal recipes Error", e)
            except Exception as e:
                print("Parse_recipes Error:", e)

    def parse_recipes_list(self, response):
        current_recipe_id = response.meta['recipe_id']
        current_recipe_url = response.meta['recipe_url']
        current_page = response.meta['page']
        if response.status == 200:
            try:
                # 使用pyquery解析html
                content = response.text
                soup = BeautifulSoup(content, 'lxml')
                content = soup.prettify()
                content = pq(content, parser="html")
                # 获取recipe列表
                recipes_list = content('.recipe-stamp-list .gridRecipeStamp.gridStamp').items()
                # 获取recipe总数
                page_num = int(content('.paging-wrapper .paging-description.hidden-tablet').text().split(" ")[0])
                for recipe_item in recipes_list:
                    try:
                        # 构造每条recipe详细信息的连接
                        recipe_item_url = "https://shop.countdown.co.nz" + recipe_item(
                            '.action-button-layout.gridRecipeStamp-readButton').attr(
                            'href')
                        yield Request(url=recipe_item_url,
                                      callback=self.parse_recipe_item,
                                      dont_filter=True)
                    except Exception as e:
                        print("Traversal recipes_list Error", e)
                if current_page*24 < page_num:
                    recipes_list_url = self.recipes_list_url.format(recipe_id=current_recipe_id, recipe_url=current_recipe_url,
                                                                    page=current_page+1)
                    yield Request(url=recipes_list_url,
                                  callback=self.parse_recipes_list,
                                  meta={
                                      'recipe_id': current_recipe_id,
                                      'recipe_url': current_recipe_url,
                                      'page': current_page+1
                                  },
                                  dont_filter=True)
                else:
                    self.log_file.write("{kind}类别已爬取完，一共爬取{page}页\n".format(kind=current_recipe_url, page=current_page))
            except Exception as e:
                print("Parse_recipes_list Error:", e)
        else:
            self.log_file.write("链接:{url},状态:{status}\n".format(url=response.url, status=response.status))

    def parse_recipe_item(self, response):
        if response.status == 200:
            try:
                content = response.text
                soup = BeautifulSoup(content, 'lxml')
                content = soup.prettify()
                content = pq(content, parser="html")
                item = RecipesItem()
                # 获取ingredients文本
                recipe_ingredients_uls = content('.recipe-ingredients ul').items()
                # 先将字段初始化，避免某些recipe信息不全造成异常
                item['ingredients'] = ""
                item['methods'] = ""
                ingredients_text = ""
                for ul in recipe_ingredients_uls:
                    try:
                        lis = ul('li').items()
                        for li in lis:
                            ingredients_text = ingredients_text + li.text() + ";"
                    except Exception as e:
                        print("Traversal recipe_ingredients_uls Error", e)
                ingredients_text = ingredients_text.strip(";")
                item['ingredients'] = ingredients_text
                # 获取methods字段
                methods_ps = content('.recipe-directions._noajax .recipe-content').items()
                methods_text = ""
                for method_p in methods_ps:
                    method_text = method_p.text()
                    if method_text != "":
                        methods_text = methods_text + method_text + ";"
                methods_text = methods_text.strip(";")
                item['methods'] = methods_text
                item['url'] = response.url
                item['file_name']= self.recipes_file_name
                yield item
            except Exception as e:
                print("Parse_recipe_item Error:", e)
        else:
            self.log_file.write("链接:{url},状态:{status}\n".format(url=response.url, status=response.status))


if __name__ == '__main__':
    cmdline.execute("scrapy crawl recipes_spider".split())
