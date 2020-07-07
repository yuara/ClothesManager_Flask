# -*- coding: utf-8 -*-
import re
import datetime
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from project import create_app, db
from project.models import Forecast, Location


class ForecastItem(scrapy.Item):
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


class ForecastSpider(CrawlSpider):
    name = "forecast"
    allowed_domains = ["tenki.jp"]
    start_urls = ["https://tenki.jp/indexes/dress/"]

    rules = (
        Rule(LinkExtractor(allow=r"/indexes/dress/\d+/\d+/"), callback="parse_item"),
    )

    def parse_item(self, response):
        item = ForecastItem()

        place = response.css("#delimiter ol li a span::text").extract()
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


class ForecastPipeline(object):
    def __init__(self):
        app = create_app()
        app.app_context().push()
        self.progress = 0
        self.scraped = 0
        self.err = 0

    def process_item(self, item, spider):

        update_time = item["update_time"]
        update_time = int(re.findall(r"\d{2}", update_time)[1])
        today = datetime.datetime.today()
        update_time = datetime.datetime(
            year=today.year, month=today.month, day=today.day, hour=update_time
        )

        prefecture = item["prefecture"]
        city = item["weather_city"][0]

        location = Location.query.filter_by(
            pref_name=prefecture, city_name=city
        ).first()
        if location is None:
            self.err += 1
            self.progress += 1
            print(f"scraped/error/progress: {self.scraped}/{self.err}/{self.progress}")
            raise scrapy.exceptions.DropItem("Wrong location scraped.")

        latest_forecast_data = Forecast.query.filter_by(
            location_id=location.id, update_time=update_time
        ).first()
        if latest_forecast_data:
            self.err += 1
            self.progress += 1
            print(f"scraped/error/progress: {self.scraped}/{self.err}/{self.progress}")
            raise scrapy.exceptions.DropItem("Already inserted this items.")

        else:
            clothes_city_list = item["clothes_info"][::2]
            clothes_index_list = item["clothes_info"][1::2]

            weather = item["weather"][0]
            highest_temp = int(item["highest_temp"][0][:-1])
            lowest_temp = int(item["lowest_temp"][0][:-1])

            rain_chance = item["rain_chance"][0]
            rain_chance = int(
                rain_chance.replace("\n        ", "").replace("%    ", "")
            )

            i = clothes_city_list.index(city)
            clothes_index = clothes_index_list[i]

            forecast = Forecast(
                location_id=location.id,
                weather=weather,
                highest_temp=highest_temp,
                lowest_temp=lowest_temp,
                rain_chance=rain_chance,
                clothes_index=clothes_index,
                update_time=update_time,
            )
            db.session.add(forecast)
            db.session.commit()

            self.scraped += 1
            self.progress += 1
            return f"scraped/error/progress: {self.scraped}/{self.err}/{self.progress}"
