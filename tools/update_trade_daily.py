#coding=utf-8

import numpy as np
import codecs
import pandas as pd
import datetime
import talib as ta 
import dbconfig
import pymysql
import math
import matplotlib.pyplot as plt

from jqdatasdk import *


def update_trade_daily_jq(start_date = None, end_date_str = None):
	table_name = "trade_daily_jq"
	
	if start_date == None:
		today_time_temp = datetime.datetime.now() - datetime.timedelta(days=0)
		start_date = today_time_temp.strftime('%Y-%m-%d')

	if end_date_str == None:
		today_time_temp = datetime.datetime.now() - datetime.timedelta(days=0)
		end_date_str = today_time_temp.strftime('%Y-%m-%d')
	
	db = pymysql.connect(host = dbconfig.DB_HOST, user= dbconfig.DB_USER, 
		passwd= dbconfig.DB_PWD, db= dbconfig.DB_NAME, charset='utf8')
		
	cursor = db.cursor()
	
	auth(dbconfig.JQNAME, dbconfig.JQPWD)

	stock_list = get_all_securities().index
	

	flag = False
	for stock_code in stock_list:

		print(stock_code)
		flag = True
		ts_code = stock_code
		price = get_price(ts_code,  start_date=start_date, end_date=end_date_str, frequency="daily")
		
		i = 0
		date_list = price.index
		for p in price.values:

			date_str = str(date_list[i]).split(" ")[0]
			if math.isnan(p[0]) or math.isnan(p[1]) or math.isnan(p[2]) or math.isnan(p[3]) or math.isnan(p[4]):
				i += 1
				continue
				
			sql = "INSERT INTO " + table_name + \
				" (ts_code, date, open, close, high, low, volume, money) \
				VALUES (\"%s\", \"%s\",\"%f\", \"%f\", \"%f\", \"%f\", \"%f\", \"%f\")"   % \
				(stock_code, date_str, p[0], p[1], p[2], p[3], p[4], p[5])
		
			try:
				cursor.execute(sql)
				db.commit()
			except Exception as ex:
				print(ex)
				print("insert into database error. sql is %s" % sql)
				db.rollback()
			finally:
				i += 1
	print("insert all data to database complete")
	db.close()
	


if __name__ == "__main__":
	#update_trade_daily_jq()
	
	
	update_trade_daily_jq("2021-02-6")
	
	