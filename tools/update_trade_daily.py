#coding=utf-8

import numpy as np
import codecs
import pandas as pd
import datetime
import talib as ta 
import dbconfig
import pymysql
import matplotlib.pyplot as plt

from jqdatasdk import *


def update_trade_daily_jq(start_date = None):
	table_name = "trade_daily_jq"
	
	if start_date == None:
		start_date = "2005-01-01"

	yesterday_time_temp = datetime.datetime.now() - datetime.timedelta(days=1)
	yesterday_date_str = yesterday_time_temp.strftime('%Y-%m-%d')
	
	db = pymysql.connect(host = dbconfig.DB_HOST, user= dbconfig.DB_USER, 
		passwd= dbconfig.DB_PWD, db= dbconfig.DB_NAME, charset='utf8')
		
	cursor = db.cursor()
	
	auth(dbconfig.JQNAME, dbconfig.JQPWD)

	stock_list = get_all_securities().index
	

	flag = False
	for stock_code in stock_list:

		if stock_code != "600363.XSHG" and flag == False:
			continue

		flag = True
		ts_code = stock_code
		price = get_price(ts_code,  start_date=start_date, end_date=yesterday_date_str, frequency="daily")
		
		i = 0
		date_list = price.index
		for p in price.values:

			date_str = str(date_list[i]).split(" ")[0]
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
	update_trade_daily_jq()
	