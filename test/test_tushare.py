import tushare as ts

ts.set_token('')
pro = ts.pro_api()


'''
df = pro.trade_cal(exchange='SSE', is_open='1', 
                            start_date='20200101', 
                            end_date='20200401', 
                            fields='cal_date')
'''


df = pro.index_dailybasic( ts_code='000300.SH', start_date='20130101', fields='ts_code,trade_date,turnover_rate,pe,pe_ttm')

date=df['trade_date']

pe = df['pe_ttm']


with open('./000300.csv','a+') as f:
	for index in pe.index:
		f.write(str(date[index])+','+str(pe[index])+'\n')



