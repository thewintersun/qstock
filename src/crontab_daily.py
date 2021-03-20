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
from stock import *
		
		
if __name__ == "__main__":
	good_stock_file = "../data/good_stock2.txt"
	stock_list = []
	
	today_time_temp = datetime.datetime.now() - datetime.timedelta(days=0)
	today_date_str = today_time_temp.strftime('%Y-%m-%d')
	print(today_date_str)
	
	start_date = "2019-08-01"
	end_date = today_date_str


	with codecs.open(good_stock_file, 'r', 'utf-8') as fr:
		for line in fr:
			ts_code = line.strip().split()[1]
			s = Stock(ts_code)
			s.read_data(start_date, end_date)
			stock_list.append(s)
	
	sell_stock_list = []

	buy_stock_list = []
	
	for s in stock_list:
		last_index = len(s.macd_data.close_price_list)
		print(s.ts_code)
		is_buy = s.is_buy(last_index)
		if is_buy == 1:
			buy_stock_list.append(s.ts_code)
	
	with codecs.open("../data/buy_stock_list.txt", 'w', 'utf-8') as fw:
		for code in buy_stock_list:
			fw.write(code.split('.')[0] + '\r\n')
	
	for s in stock_list:
		last_index = len(s.macd_data.close_price_list)
		print(s.ts_code)
		s.flag_buy = True
		is_sell = s.is_sell(last_index)
		if is_sell == 1:
			sell_stock_list.append(s.ts_code)
	
	with codecs.open("../data/sell_stock_list.txt", 'w', 'utf-8') as fw:
		with codecs.open("../data/buyed.txt", 'r', 'utf-8') as fr:
			buyed_list = []
			print()
			print()
			print("Buyed stock in sell is:")
			for line in fr:
				buyed_list.append(line.strip())
			for code in sell_stock_list:
				fw.write(code.split('.')[0] + '\r\n')
				
				if code.split('.')[0] in buyed_list:
					print(code.split('.')[0])