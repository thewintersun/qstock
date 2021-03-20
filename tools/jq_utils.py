#coding=utf-8

import dbconfig
import pymysql
import codecs

def get_stock_code_from_name(name):
	table_name = "stock_list_jq"
	
	db = pymysql.connect(host = dbconfig.DB_HOST, user= dbconfig.DB_USER, 
		passwd= dbconfig.DB_PWD, db= dbconfig.DB_NAME, charset='utf8')		
	cursor = db.cursor()
	
	sql = "select ts_code, symbol, start_date from " + table_name + " where display_name='" + name + "'"

	try:
		cursor.execute(sql)
		result = cursor.fetchall()

		if len(result) > 0:
			return result[0][0], result[0][1], result[0][2]
	except Exception as ex:
		print(ex)
	db.close()
	return "","",""
	
if __name__ == "__main__":
	with codecs.open("../data/good_stock.txt", 'r', 'utf-8') as fr:
		with codecs.open("../data/good_stock2.txt", 'w', 'utf-8') as fw:
			for line in fr:
				ts_code, code, start_date = get_stock_code_from_name(line.strip())
				if start_date < "2019-05-01":
					fw.write(line.strip() + '\t' + ts_code + '\r\n')
			