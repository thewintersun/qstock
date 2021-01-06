#coding=utf-8

import numpy as np
import pandas as pd
import talib as ta 
import matplotlib.pyplot as plt
import dbconfig
import pymysql

from jqdatasdk import *





def update_stock_list_jq():
	table_name = "stock_list_jq"
	
	db = pymysql.connect(host = dbconfig.DB_HOST, user= dbconfig.DB_USER, 
		passwd= dbconfig.DB_PWD, db= dbconfig.DB_NAME, charset='utf8')
		
	cursor = db.cursor()
	
	auth(dbconfig.JQNAME, dbconfig.JQPWD)

	df = get_all_securities()
	

	i = 0
	for v in df.values:
		symbol = df.index[i].split(".")[0]
		
		sql = "INSERT INTO " + table_name + \
			" (ts_code, symbol, display_name, name, start_date, end_date, type) \
			VALUES (\"%s\", \"%s\",\"%s\", \"%s\", \"%s\", \"%s\", \"%s\")"   % \
			(df.index[i],symbol, v[0], v[1], v[2], v[3],v[4])
		#print(sql)
		try:
			cursor.execute(sql)
			db.commit()
		except Exception as ex:
			print(ex)
			print("insert into database error. sql is %s" % sql)
			db.rollback()
		finally:
			i += 1
	print("insert all data to database complete, all number is %d" % len(df.values))
	db.close()

	
if __name__ == "__main__":
	update_stock_list_jq()
	pass