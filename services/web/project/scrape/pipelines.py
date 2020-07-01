import re
import scrapy
import datetime
from project import create_app, db
from project.models import Tenki

app = create_app()
app.app_context().push()


class ValidationPipeline(object):
    def process_item(self, item, spider):
        if len(item) == 50:
            raise scrapy.exceptions.DropItem("Scraped less than 50 items.")
        elif len(item) > 50:
            raise scrapy.exceptions.DropItem("Scraped more than 50 items.")
        else:
            return item


class TenkiPipeline(object):
    def __init__(self):
        self.progress = 0

    def process_item(self, item, spider):

        clothes_city_list = item["clothes_info"][::2]
        clothes_index_list = item["clothes_info"][1::2]
        area = item["area"]
        prefecture = item["prefecture"]

        update_time = item["update_time"]
        update_time = int(re.findall(r"\d{2}", update_time)[1])
        today = datetime.datetime.today()
        update_time = datetime.datetime(
            year=today.year, month=today.month, day=today.day, hour=update_time
        )

        newest_tenki_data = Tenki.query.filter_by(update_time=update_time).all()
        if len(newest_tenki_data) >= 50:
            self.progress += 1
            print(self.progress)
            raise scrapy.exceptions.DropItem("Already inserted this items.")

        else:
            city = item["weather_city"][0]
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

        return item
