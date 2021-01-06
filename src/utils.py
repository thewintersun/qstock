#coding=utf-8

import datetime

'''
找出周线数据中，当前时间点之前的数据list
'''
def find_before_weekly_data(week_list, date):
	if len(week_list) == 0:
		return 0
	if date <= week_list[0]:
		return 0
	
	for i in range(len(week_list)):
		if date > week_list[i]:
			continue
		if date <= week_list[i]:
			return i
			
	lastday = week_list[-1]
	y = lastday.split("-")[0]
	m = lastday.split("-")[1]
	d = lastday.split("-")[2]
	lastdaytime = datetime.date(int(y), int(m), int(d))
	
	y = date.split("-")[0]
	m = date.split("-")[1]
	d = date.split("-")[2]
	datedaytime = datetime.date(int(y), int(m), int(d))

	if abs((datedaytime - lastdaytime).days) <= 7:
		return len(week_list)-1

	return 0
