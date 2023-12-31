import calendar
import codecs
import datetime
import math
import os

import pandas as pd
import requests


class Calendar:
    def fetch_wallpaper(self):
        url = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=zh-CN"
        response = requests.get(url).json()["images"][0]
        image = response["urlbase"]
        date = response["startdate"]
        real_date = datetime.datetime.strptime(date, "%Y%m%d") + datetime.timedelta(days=1)

        self.day = real_date.strftime("%Y%m%d")
        self.month = self.day[:6]
        self.thumbnail = f"https://www.bing.com{image}_320x240.jpg"
        self.uhd = f"https://www.bing.com{image}_UHD.jpg"
        self.title = response["title"]
        self.place = response["copyright"].split(" (")[0]
        self.storage = os.path.join(self.month, "data.json")

        return self

    def check_file(self):
        os.makedirs(self.month, exist_ok=True)

        if os.path.isfile(self.storage):
            self.data = pd.read_json(self.storage)
        else:
            now = datetime.datetime.now()
            first_day, total_days = calendar.monthrange(now.year, now.month)
            week_name = ["一", "二", "三", "四", "五", "六", "日"]
            total_weeks = math.ceil((first_day + total_days) / 7)
            self.data = pd.DataFrame(data="", columns=week_name, index=range(total_weeks))

        return self

    def fill_content(self):
        current_day = datetime.datetime.strptime(self.day, "%Y%m%d")
        current_day_of_week = int(current_day.strftime("%w")) - 1
        week_number = int(current_day.strftime("%W")) - int(current_day.replace(day=1).strftime("%W"))

        content = f'[![]({self.thumbnail} "{self.place}")]({self.uhd})<br>{self.day[4:]}<br>{self.title}'
        self.data.iloc[week_number, current_day_of_week] = content

        self.data.to_json(self.storage)
        self.data.to_markdown(os.path.join(self.month, "README.md"), index=False)

        file_list = [
            os.path.join(parent, file)
            for parent, _, files in os.walk(".")
            for file in files
            if os.path.splitext(file)[0] == "README" and parent != "."
        ]

        with codecs.open("README.md", "w", "utf-8") as f:
            f.write("# 每日壁纸\n\n")
            f.write(f"## {self.day} - {self.title}\n\n")
            f.write(f"###### {self.place}\n\n")
            f.write(f"![]({self.uhd})\n\n")
            f.write("## 归档\n\n")
            for file in sorted(file_list, reverse=True):
                file = file[1:].replace("\\", "/")
                f.write(f"| [{file[1:7]}]({file})\n")
            f.write("|")


Calendar().fetch_wallpaper().check_file().fill_content()
