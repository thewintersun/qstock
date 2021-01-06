#coding=utf-8

import numpy as np
import codecs
import pandas as pd
import datetime
import talib as ta 
import matplotlib.pyplot as plt

from jqdatasdk import *
auth('18516238498', '7788521Jq')



yesterday_time_temp = datetime.datetime.now() - datetime.timedelta(days=4)
yesterday_date_str = yesterday_time_temp.strftime('%Y-%m-%d')

print(yesterday_date_str)




#price = get_price("000002.XSHE", start_date="2020-08-01", end_date="2020-12-25", frequency="daily", fields=['close'])['close']
price = get_bars("000001.XSHE", 12, unit='1w',end_dt=yesterday_date_str)
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