import calendar
import codecs
import datetime
import os

import pandas as pd
import requests


class 日历:
    def 获取壁纸(本):
        网址 = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=zh-CN"
        壁纸 = requests.get(网址).json()["images"][0]
        图片 = 壁纸["urlbase"]

        本.日期 = 壁纸["startdate"]
        本.月份 = 壁纸["startdate"][:6]
        本.缩略图 = f"https://www.bing.com{图片}_320x240.jpg"
        本.高清图 = f"https://www.bing.com{图片}_UHD.jpg"
        本.标题 = 壁纸["title"]
        本.存储 = os.path.join(本.月份, "data.json")

        return 本

    def 检查文件(本):
        os.makedirs(本.月份, exist_ok=True)

        if os.path.isfile(本.存储):
            本.数据 = pd.read_json(本.存储)
        else:
            此时 = datetime.datetime.now()
            该月第一天是星期几, 该月一共有几天 = calendar.monthrange(此时.year, 此时.month)
            星期名称 = ["一", "二", "三", "四", "五", "六", "日"]
            本月周数 = int((该月第一天是星期几 + 该月一共有几天) / 7) + 1
            本.数据 = pd.DataFrame(data="", columns=星期名称, index=range(本月周数))

        return 本

    def 填写文件(本):
        当天日期 = datetime.datetime.strptime(本.日期, "%Y%m%d")
        当天星期几 = int(当天日期.strftime("%w")) - 1

        当天周数 = int(当天日期.strftime("%W"))
        一号周数 = int(当天日期.replace(day=1).strftime("%W"))
        本月第几周 = 当天周数 - 一号周数

        内容 = f"[![]({本.缩略图})]({本.高清图})<br>{本.日期[4:]}<br>{本.标题}"
        本.数据.iloc[本月第几周, 当天星期几] = 内容

        本.数据.to_json(本.存储)
        本.数据.to_markdown(os.path.join(本.月份, "README.MD"), index=False)

        文件列表 = [
            os.path.join(父目录, 当前文件名)
            for 父目录, _, 文件名 in os.walk(".")
            for 当前文件名 in 文件名
            if os.path.splitext(当前文件名)[0] == "README" and 父目录 != "."
        ]

        with codecs.open("README.md", "w", "utf-8") as 文:
            文.write("# 每日壁纸\n\n")
            文.write(f"## {本.日期} - {本.标题}\n\n")
            文.write(f"![]({本.高清图})\n\n")
            文.write("## 归档\n\n")
            for 文件名 in sorted(文件列表, reverse=True):
                文件名 = 文件名[1:].replace("\\", "/")
                文.write(f"| [{文件名[1:7]}]({文件名})\n")
            文.write("|")


日历().获取壁纸().检查文件().填写文件()
