#coding=utf-8

'''
获取市盈率各种指标比较好的优质股名单，写入good_stock.txt

'''
import numpy as np
import codecs
import pandas as pd
import datetime
import talib as ta 
import matplotlib.pyplot as plt

from jqdatasdk import *
from jqdatasdk import finance


auth('18516238498', '7788521Jq')

output_filename = "good_stock.txt"

q=query(
        finance.STK_INCOME_STATEMENT.code,
        finance.STK_INCOME_STATEMENT.pub_date,
        finance.STK_INCOME_STATEMENT.net_profit,
		finance.STK_INCOME_STATEMENT.total_profit,
		finance.STK_INCOME_STATEMENT.basic_eps,
		finance.STK_INCOME_STATEMENT.total_operating_revenue).filter(finance.STK_INCOME_STATEMENT.code=='600519.XSHG',
		finance.STK_INCOME_STATEMENT.pub_date>='2020-01-01',
		finance.STK_INCOME_STATEMENT.report_type==0).limit(20)
df=finance.run_query(q)
print(df)
