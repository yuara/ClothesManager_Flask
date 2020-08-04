# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import re
import datetime
import scrapy
import pymysql


class ForecastPipeline:
    def __init__(self):
        # Connect to mysql
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

    def close_spider(self, spider):
        self.connection.close()

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

        # Check if a location of scraped data is in the database
        location_sql = "SELECT * FROM location WHERE area_name=%s AND pref_name=%s AND city_name=%s"
        self.cursor.execute(location_sql, (area, prefecture, city))
        location = self.cursor.fetchone()
        if location is None:
            raise scrapy.exceptions.DropItem("Invalid location.")

        # Check if scraped data is new one
        latest_forecast_sql = (
            "SELECT * FROM forecast WHERE location_id=%s AND update_time=%s"
        )
        self.cursor.execute(latest_forecast_sql, (location["id"], update_time))
        latest_forecast_data = self.cursor.fetchone()
        if latest_forecast_data:
            raise scrapy.exceptions.DropItem("Already inserted this items.")

        clothes_city_list = item["clothes_info"][::2]
        clothes_index_list = item["clothes_info"][1::2]

        weather = item["weather"][0]
        highest_temp = int(item["highest_temp"][0][:-1])
        lowest_temp = int(item["lowest_temp"][0][:-1])
        rain_chance = item["rain_chance"][0]
        rain_chance = int(rain_chance.replace("\n        ", "").replace("%    ", ""))
        i = clothes_city_list.index(city)
        index = clothes_index_list[i]

        # Check if a scraped index value is in the database
        clothes_index_sql = "SELECT id FROM clothes_index WHERE value=%s"
        self.cursor.execute(clothes_index_sql, (index,))
        clothes_index = self.cursor.fetchone()
        if clothes_index is None:
            raise scrapy.exceptions.DropItem("Invalid clothes index")

        location_id = location["id"]
        clothes_index_id = clothes_index["id"]

        # Insert scraped data into the database
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

        return f"Scraped {self.counter}/{update_time}"
