#coding=utf-8

import numpy as np
import codecs
import pandas as pd
import datetime
import talib as ta 
import matplotlib.pyplot as plt

from jqdatasdk import *
auth('18516238498', '')

'''
df = get_fundamentals(query(
        valuation.code,  valuation.pe_ratio,indicator.adjusted_profit, indicator.roe,indicator.statDate,indicator.inc_return
    ).filter(
		valuation.code == '000001.XSHE',
        #valuation.pe_ratio < 50,
		#indicator.roe > 6
		#valuation.roe > 0.2,
    ).order_by(
        # 按市值降序排列
        valuation.market_cap.desc()
    ).limit(
        # 最多返回100个
        1000
    ), date='2020-01-09')
print(df)


'''
yesterday_time_temp = datetime.datetime.now() - datetime.timedelta(days=0)
yesterday_date_str = yesterday_time_temp.strftime('%Y-%m-%d')




#price = get_price("000002.XSHE", start_date="2021-01-01", end_date="2021-01-19", frequency="daily", fields=['close'])['close']
price = get_bars("000001.XSHE", 3, unit='1w',end_dt=yesterday_date_str)
value_list = price.values
print(price)

'''
dif, dea, hist = ta.MACD(price,fastperiod=12, slowperiod=26)
print(hist)
print(hist.index)

plt.figure(figsize=(18,8))
ax1 = plt.subplot(2,1,1)
ax1.plot(price)
ax2 = plt.subplot(2,1,2)
ax2.plot(dif)
ax2.plot(dea)


ax2.bar(x=hist.index, height=hist)
plt.show()

'''