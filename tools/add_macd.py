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



def calc_macd(ts_code):
	db = pymysql.connect(host = dbconfig.DB_HOST, user= dbconfig.DB_USER, 
		passwd= dbconfig.DB_PWD, db= dbconfig.DB_NAME, charset='utf8')
		
	cursor = db.cursor()
	sql = "select * from trade_daily_jq where ts_code = '" + ts_code + "' order by Id asc"
	cursor.execute(sql)
	result = cursor.fetchall()
	close_price_list = []
	id_list = []
	for i in result:
		close_price_list.append(i[4])
		id_list.append(i[0])
	db.close()
	
	if len(close_price_list) != 0:
		price = np.array(close_price_list)

		dif, dea, hist = ta.MACD(price,fastperiod=12, slowperiod=26)
		'''
		plt.figure(figsize=(18,8))
		ax1 = plt.subplot(2,1,1)
		ax1.plot(price)
		ax2 = plt.subplot(2,1,2)
		ax2.plot(dif)
		ax2.plot(dea)
		ax2.bar(range(len(hist)), height=hist)
		'''
		return id_list,dif, dea, hist
	return [],[],[],[]

def update_macd_data(id_list, dif_list, dea_list, hist_list):
	db = pymysql.connect(host = dbconfig.DB_HOST, user= dbconfig.DB_USER, 
		passwd= dbconfig.DB_PWD, db= dbconfig.DB_NAME, charset='utf8')
	cursor = db.cursor()
	
	if len(id_list) != len(dif_list) \
		or len(id_list) != len(dea_list) \
		or len(id_list) != len(hist_list):
		print("len not same. ", len(id_list), len(dif_list), len(dea_list), len(hist_list))
		exit(0)
	
	for i in range(len(id_list)):
		id = id_list[i]
		dif = dif_list[i]
		dea = dea_list[i]
		hist = hist_list[i]
		sql = "update trade_daily_jq set macd_dif="+ str(dif) + ", macd_dea="+ str(dea) + ", macd_hist=" + str(hist) + " where Id=" + str(id)

		try:
			cursor.execute(sql)
			db.commit()
		except Exception as ex:
			print(ex)
			print("update trade_daily_jq error. sql is %s" % sql)
			db.rollback()
	db.close()
	
		
def update_all_macd():
	db = pymysql.connect(host = dbconfig.DB_HOST, user= dbconfig.DB_USER, 
		passwd= dbconfig.DB_PWD, db= dbconfig.DB_NAME, charset='utf8')
	cursor = db.cursor()

	sql = "select DISTINCT(ts_code) from stock_list_jq"
	cursor.execute(sql)
	result = cursor.fetchall()
	db.close()
	for ts_code in result:
		print(ts_code[0])
		id_list, dif_list, dea_list, hist_list = calc_macd(ts_code[0])
		update_macd_data(id_list, dif_list, dea_list, hist_list)
	
	
if __name__ == "__main__":
	update_all_macd()
	