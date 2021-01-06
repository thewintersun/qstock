#coding=utf-8
import datetime

start_date = "2020-10-09"
year  = start_date.split("-")[0]
month = start_date.split("-")[1]
day   = start_date.split("-")[2]
startday_dd = datetime.date(int(year), int(month), int(day))
yesterday_time_temp = startday_dd - datetime.timedelta(days=4)
print(yesterday_time_temp)

a = datetime.date(2017, 3, 22)
b = datetime.date(2017, 3, 25)
print((a - b).days)

