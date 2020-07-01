# -*- coding: utf-8 -*-
import re
import datetime
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from project.models import Tenki


class TenkiItem(scrapy.Item):
    area = scrapy.Field()
    prefecture = scrapy.Field()
    clothes_info = scrapy.Field()
    weather = scrapy.Field()
    highest_temp = scrapy.Field()
    lowest_temp = scrapy.Field()
    rain_chance = scrapy.Field()
    update_time = scrapy.Field()
    weather_city = scrapy.Field()

    city = scrapy.Field()
    clothes_index = scrapy.Field()


class TenkiSpider(CrawlSpider):
    name = "tenki"
    allowed_domains = ["tenki.jp"]
    start_urls = ["https://tenki.jp/indexes/dress/"]

    rules = (
        Rule(LinkExtractor(allow=r"/indexes/dress/\d+/\d+/"), callback="parse_item"),
    )

    def parse_item(self, response):
        item = TenkiItem()

        place = response.css("#delimiter ol li a span::text").extract()
        item["area"] = place[-2]
        item["prefecture"] = place[-1]

        item["update_time"] = response.css(".date-time ::text").extract_first()

        item["clothes_info"] = response.css(".map-wrap ul span ::text").extract()

        for forecast in response.css(".sub-column-forecast-pickup"):
            item["weather_city"] = forecast.css(".name ::text").extract()
            item["weather"] = forecast.css("img::attr(alt)").extract()

            item["highest_temp"] = forecast.css(
                ".date-value .high-temp ::text"
            ).extract()
            item["lowest_temp"] = forecast.css(".date-value .low-temp ::text").extract()

            item["rain_chance"] = forecast.css(".precip ::text").extract()

        yield item
