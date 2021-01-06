#coding=utf-8

import tushare as ts
import datetime
import pymysql
import dbconfig



def update_stock_list():
	table_name = "stock_list"
	
	db = pymysql.connect(host = dbconfig.DB_HOST, user= dbconfig.DB_USER, 
		passwd= dbconfig.DB_PWD, db= dbconfig.DB_NAME, charset='utf8')
		
	cursor = db.cursor()
	
	start_dt = '20100101'
	yesterday_time_temp = datetime.datetime.now() - datetime.timedelta(days=1)
	yesterday_date_str = yesterday_time_temp.strftime('%Y%m%d')
	

	ts.set_token(dbconfig.TS_TOKEN)
	pro = ts.pro_api()
	df = pro.stock_basic(exchange='', 
		fields='ts_code,symbol,name,area,industry,fullname,enname,market,exchange,curr_type,list_status,list_date,delist_date,is_hs')

	for v in df.values:
		sql = "INSERT INTO " + table_name + \
			" (ts_code,symbol,name,area,industry,fullname,enname,market,exchange, \
			curr_type,list_status,list_date,delist_date,is_hs) \
			VALUES (\"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\")"   % \
			(v[0], v[1], v[2], v[3],v[4], v[5], v[6],v[7], v[8], v[9],v[10], v[11], v[12],v[13])
		#print(sql)
		try:
			cursor.execute(sql)
			db.commit()
		except Exception as ex:
			print(ex)
			print("insert into database error. sql is %s" % sql)
			db.rollback()
	print("insert all data to database complete, all number is %d" % len(df.values))
	db.close()
	
if __name__ == "__main__":
	update_stock_list()
