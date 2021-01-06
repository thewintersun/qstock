#coding=utf-8

import numpy as np
import codecs
import pandas as pd
import datetime
import talib as ta 
import matplotlib.pyplot as plt
import math
import pymysql
import dbconfig
import strategy
import utils

class MacdData:
	def __init__(self):
		self.close_price_list = []
		self.macd_dif_list = []
		self.macd_dea_list = []
		self.macd_hist_list = []
		self.date_list = []
		self.open_price_list = []
		
		self.week_close_price_list = []
		self.week_macd_dif_list = []
		self.week_macd_dea_list = []
		self.week_macd_hist_list = []
		self.week_date_list = []
		self.week_open_price_list = []
	
class Stock:
	def __init__(self, ts_code):
		self.ts_code = ts_code
		self.flag_buy = False
		self.total_money = 100000.0 #10w
		self.buy_price = 0.0
		self.stock_number = 0

	
	
	def read_daily_data(self, ts_code, start_date, end_date):
		db = pymysql.connect(host = dbconfig.DB_HOST, user= dbconfig.DB_USER, 
		passwd= dbconfig.DB_PWD, db= dbconfig.DB_NAME, charset='utf8')
		cursor = db.cursor()
		
		sql = "select  close, macd_dif, macd_dea, macd_hist, date, open from trade_daily_jq where date>='" \
			+ start_date + "' and date <= '" + end_date + "' and ts_code='" + ts_code + "'"
		cursor.execute(sql)
		result = cursor.fetchall()
		db.close()
		
		close_price_list = []
		macd_dif_list = []
		macd_dea_list = []
		macd_hist_list = []
		date_list = []
		open_price_list = []
		
		for line in result:
			close_price_list.append(line[0])
			macd_dif_list.append(line[1])
			macd_dea_list.append(line[2])
			macd_hist_list.append(line[3])
			date_list.append(line[4])
			open_price_list.append(line[5])
		
		return close_price_list,macd_dif_list,macd_dea_list,macd_hist_list, date_list, open_price_list
		
		
	def read_weekly_data(self, ts_code, start_date, end_date):
		db = pymysql.connect(host = dbconfig.DB_HOST, user= dbconfig.DB_USER, 
		passwd= dbconfig.DB_PWD, db= dbconfig.DB_NAME, charset='utf8')
		cursor = db.cursor()
		
		sql = "select  close, macd_dif, macd_dea, macd_hist, date, open from trade_weekly_jq where date>='" \
			+ start_date + "' and date <= '" + end_date + "' and ts_code='" + ts_code + "'"
		cursor.execute(sql)
		result = cursor.fetchall()
		db.close()
		
		close_price_list = []
		macd_dif_list = []
		macd_dea_list = []
		macd_hist_list = []
		date_list = []
		open_price_list = []
		
		for line in result:
			close_price_list.append(line[0])
			macd_dif_list.append(line[1])
			macd_dea_list.append(line[2])
			macd_hist_list.append(line[3])
			date_list.append(line[4])
			open_price_list.append(line[5])
		
		return close_price_list,macd_dif_list,macd_dea_list,macd_hist_list, date_list, open_price_list
		
	
	def read_data(self, ts_code, start_date, end_date):
		macd_data = MacdData()
		macd_data.close_price_list,macd_data.macd_dif_list, macd_data.macd_dea_list, \
		macd_data.macd_hist_list, macd_data.date_list, macd_data.open_price_list \
			= self.read_daily_data(self.ts_code, start_date, end_date)
		
		year  = start_date.split("-")[0]
		month = start_date.split("-")[1]
		day   = start_date.split("-")[2]
		startday_dd = datetime.date(int(year), int(month), int(day))
		startday_temp = startday_dd - datetime.timedelta(days=70)
		start_date = startday_temp.strftime('%Y-%m-%d')

		macd_data.week_close_price_list, macd_data.week_macd_dif_list, macd_data.week_macd_dea_list, \
		macd_data.week_macd_hist_list, macd_data.week_date_list, macd_data.week_open_price_list \
			= self.read_weekly_data(self.ts_code, start_date, end_date)
			
		return macd_data
		
	def test(self, start_date, end_date):
		
		macd_data = self.read_data(self.ts_code, start_date, end_date)

		for i in range(10, len(macd_data.close_price_list)-2):
			print(macd_data.date_list[i])
			if self.flag_buy == False:
				
				
				is_buy = self.is_buy(i+1, macd_data)
				if is_buy == 1:
				
					self.flag_buy = True
					# next day open price buy it
					
					self.buy_price = macd_data.open_price_list[i+1]
					self.stock_number = (int(self.total_money / (self.buy_price * 100))) * 100
					self.total_money = self.total_money - self.stock_number * self.buy_price
					
					print("buy date: ", macd_data.date_list[i+1])
					print("buy price: ", self.buy_price)
					print("buy stock_number: ", self.stock_number)
					print("total money: ", self.total_money)					
			else:
				is_sell = self.is_sell(i+1, macd_data)
				
				if is_sell == 1:
					self.flag_buy = False
					price_diff = macd_data.close_price_list[i] - self.buy_price
					self.total_money =  self.total_money + macd_data.close_price_list[i] * self.stock_number
					self.stock_number = 0
					print("----sell date: ", macd_data.date_list[i])
					print("----sell price: ", macd_data.close_price_list[i])
					print("----price_diff = ", price_diff)
					print("----total money: ", self.total_money)
					
		print("The final money is %d" % (self.total_money + self.stock_number * macd_data.open_price_list[len(macd_data.close_price_list)-1]))
		
	'''
	return:
		1: 买
		0: 不买
	'''
		
	def is_buy(self, index, macd_data):
		price_list = macd_data.close_price_list[:index]
		dif_list = macd_data.macd_dif_list[:index]
		dea_list = macd_data.macd_dea_list[:index]
		hist_list = macd_data.macd_hist_list[:index]
		
		n = utils.find_before_weekly_data(macd_data.week_date_list, macd_data.date_list[index])
		
		week_price_list     = macd_data.week_close_price_list[:n]
		week_macd_dif_list  = macd_data.week_macd_dif_list[:n]
		week_macd_dea_list  = macd_data.week_macd_dea_list[:n]
		week_macd_hist_list = macd_data.week_macd_hist_list[:n]

		if self.flag_buy:
			return 0
			
		if len(hist_list) < 10:
			print("too short hist length")
			return 0
		
		if len(hist_list) != len(price_list) or \
			len(hist_list) != len(dif_list) or \
			len(hist_list) != len(dea_list):
			print("len not the same")
			return 0
		
		max_hist = max(hist_list[-10:])
		min_hist = min(hist_list[-10:])
		

		# 如果周线级别macd快死叉，则不买
		ret, determin = strategy.check_weekly_dead_cut(week_price_list, week_macd_dif_list,week_macd_dea_list, week_macd_hist_list)
		if ret == 1 and determin:
			return 0
		
		ret, determin = strategy.buy_dif_leave_dea_too_small(dif_list, dea_list)
		if ret == 0 and determin:
			return 0
		
		ret, determin = strategy.buy_band_low_position(price_list,  dif_list, dea_list, hist_list)
		if ret == 1 and determin:
			return 1
		
		ret, determin = strategy.buy_higher_red_hist(price_list,  dif_list, dea_list, hist_list)
		if ret == 1 and determin:
			return 1
			
		return 0

		
	'''
	
	return
		1: sell
		0: not sell
	'''
	def is_sell(self, index, macd_data):
		price_list = macd_data.close_price_list[:index]
		dif_list = macd_data.macd_dif_list[:index]
		dea_list = macd_data.macd_dea_list[:index]
		hist_list = macd_data.macd_hist_list[:index]
		
		n = utils.find_before_weekly_data(macd_data.week_date_list, macd_data.date_list[index])
		week_price_list     = macd_data.week_close_price_list[:n]
		week_macd_dif_list  = macd_data.week_macd_dif_list[:n]
		week_macd_dea_list  = macd_data.week_macd_dea_list[:n]
		week_macd_hist_list = macd_data.week_macd_hist_list[:n]
		
		if not self.flag_buy:
			return 0
			
		if len(hist_list) < 10:
			print("too short hist length")
			return 0
		
		if len(hist_list) != len(price_list) or \
			len(hist_list) != len(dif_list) or \
			len(hist_list) != len(dea_list):
			print("len not the same")
			return 0
		
		ret, determin = strategy.sell_dif_leave_dea(price_list, dif_list, dea_list)
		if determin and ret == 1:
			return 1
			
		delta = self.delta(hist_list[-2], hist_list[-1])

		if delta < -0.01:
			return 1
		
		return 0

		
		
	def delta(self, last_value, new_value):
		# if bigger than 0.02 is much more
		delta = new_value - last_value
		return delta
		
		
if __name__ == "__main__":
	s = Stock("000001.XSHE")
	s.test( "2020-01-01", "2020-12-31")

	
	
	
	
	