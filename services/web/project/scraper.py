# -*- coding: utf-8 -*-
import re
import datetime
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from project import create_app, db

# from project.models import Forecast, Location, ClothesIndex
import pymysql


class ForecastItem(scrapy.Item):
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


class ForecastPipeline(object):
    def __init__(self):
        self.connection = pymysql.connect(
            host="db",
            user="ClothesManager",
            password="cm",
            db="cmdb",
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )
        self.cursor = self.connection.cursor()
        self.counter = 0

    def process_item(self, item, spider):

        update_time = item["update_time"]
        update_time = int(re.findall(r"\d{2}", update_time)[1])
        today = datetime.datetime.today()
        update_time = datetime.datetime(
            year=today.year, month=today.month, day=today.day, hour=update_time
        )

        area = item["area"]
        prefecture = item["prefecture"]
        city = item["weather_city"][0]

        location_sql = "SELECT * FROM location WHERE area_name=%s AND pref_name=%s AND city_name=%s"
        print(location_sql)
        self.cursor.execute(location_sql, (area, prefecture, city))
        # location_sql = "SELECT TOP (1) * FROM location WHERE area_name=%s AND pref_name=%s AND city_name=%s ;"
        # print(location_sql)
        # self.cursor.execute(location_sql, (area, prefecture, city))
        print("got data")
        location = self.cursor.fetchone()
        print(f"***fetch {location['id']}****")

        # location = Location.query.filter_by(
        #     pref_name=prefecture, city_name=city
        # ).first()
        if location is None:
            raise scrapy.exceptions.DropItem("Invalid location.")

        latest_forecast_sql = (
            "SELECT * FROM forecast WHERE location_id=%s AND update_time=%s"
        )
        self.cursor.execute(latest_forecast_sql, (location["id"], update_time))
        latest_forecast_data = self.cursor.fetchone()
        # latest_forecast_data = Forecast.query.filter_by(
        #     location_id=location.id, update_time=update_time
        # ).first()
        if latest_forecast_data:
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
            index = clothes_index_list[i]

            clothes_index_sql = "SELECT id FROM clothes_index WHERE value=%s"
            self.cursor.execute(clothes_index_sql, (index,))
            clothes_index = self.cursor.fetchone()

            # clothes_index = ClothesIndex.query.filter_by(value=index).first()
            if clothes_index is None:
                raise scrapy.exceptions.DropItem("Invalid clothes index")

            # location_id = location.id
            # clothes_index_id = clothes_index.id

            location_id = location["id"]
            clothes_index_id = clothes_index["id"]

            # forecast = Forecast(
            #     location_id=location_id,
            #     weather=weather,
            #     highest_temp=highest_temp,
            #     lowest_temp=lowest_temp,
            #     rain_chance=rain_chance,
            #     clothes_index_id=clothes_index_id,
            #     update_time=update_time,
            # )

            insert_sql = "INSERT INTO forecast (location_id, weather, highest_temp, lowest_temp, rain_chance, clothes_index_id, update_time) VALUES (%s, %s, %s, %s, %s, %s, %s)"

            self.cursor.execute(
                insert_sql,
                (
                    location_id,
                    weather,
                    highest_temp,
                    lowest_temp,
                    rain_chance,
                    clothes_index_id,
                    update_time,
                ),
            )
            self.connection.commit()
            self.counter += 1

            return f"Scraped {self.counter}"
