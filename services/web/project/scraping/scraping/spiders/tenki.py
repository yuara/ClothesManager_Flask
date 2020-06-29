# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class TenkiSpider(CrawlSpider):
    name = "tenki"
    allowed_domains = ["tenki.jp"]
    start_urls = ["https://tenki.jp/indexes/dress/"]

    rules = (
        Rule(LinkExtractor(allow=r"/indexes/dress/\d+/\d+/"), callback="parse_item"),
    )

    def parse_item(self, response):
        item = {}

        place = response.css("#delimiter ol li a span::text").extract()
        item["area"] = place[-2]
        item["prefecture"] = place[-1]

        item["announced_time"] = response.css(".date-time ::text").extract_first()
        item["date"] = response.css(".map-date ::text").extract_first()

        item["clothes_indexes"] = response.css(".map-wrap ul span ::text").extract()

        for forecast in response.css(".sub-column-forecast-pickup"):
            item["weather_city"] = forecast.css(".name ::text").extract()
            item["weather"] = forecast.css("img::attr(alt)").extract()

            item["high_temp"] = forecast.css(".date-value .high-temp ::text").extract()
            item["low_temp"] = forecast.css(".date-value .low-temp ::text").extract()

            item["rain_chance"] = forecast.css(".precip ::text").extract()

        yield item
