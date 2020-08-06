# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ForecastItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
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
