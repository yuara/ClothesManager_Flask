# -*- coding: utf-8 -*-
import re
import datetime
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from project import create_app, db
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


class TenkiPipeline(object):
    def __init__(self):
        app = create_app()
        app.app_context().push()
        self.progress = 0

    def process_item(self, item, spider):

        update_time = item["update_time"]
        update_time = int(re.findall(r"\d{2}", update_time)[1])
        today = datetime.datetime.today()
        update_time = datetime.datetime(
            year=today.year, month=today.month, day=today.day, hour=update_time
        )

        city = item["weather_city"][0]

        newest_tenki_data = Tenki.query.filter_by(
            city=city, update_time=update_time
        ).first()
        if newest_tenki_data:
            self.progress += 1
            print(self.progress)
            raise scrapy.exceptions.DropItem("Already inserted this items.")

        else:
            clothes_city_list = item["clothes_info"][::2]
            clothes_index_list = item["clothes_info"][1::2]
            area = item["area"]
            prefecture = item["prefecture"]

            weather = item["weather"][0]
            highest_temp = int(item["highest_temp"][0][:-1])
            lowest_temp = int(item["lowest_temp"][0][:-1])

            rain_chance = item["rain_chance"][0]
            rain_chance = int(
                rain_chance.replace("\n        ", "").replace("%    ", "")
            )

            i = clothes_city_list.index(city)
            clothes_index = clothes_index_list[i]

            item["area"] = area
            item["prefecture"] = prefecture
            item["city"] = city
            item["weather"] = weather
            item["highest_temp"] = highest_temp
            item["lowest_temp"] = lowest_temp
            item["rain_chance"] = rain_chance
            item["clothes_index"] = clothes_index
            item["update_time"] = update_time
            self.progress += 1
            print(self.progress)

            tenki = Tenki(
                area=area,
                prefecture=prefecture,
                city=city,
                weather=weather,
                highest_temp=highest_temp,
                lowest_temp=lowest_temp,
                rain_chance=rain_chance,
                clothes_index=clothes_index,
                update_time=update_time,
            )
            db.session.add(tenki)
            db.session.commit()
