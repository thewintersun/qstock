#coding=utf-8


'''
策略的函数
返回第一个值表示操作，第二个值是True表示按这个操作执行，并且调用方马上return，不用等后续的判断了
'''

'''
判断是否是卖点，
主要逻辑：在dif线从下往上离dea线越来越近，突然又往下拐了的情况，这种情况卖出
dif 在0下方的情况
'''
def sell_dif_leave_dea(price_list, dif_list, dea_list):
	d4 = dif_list[-4] - dea_list[-4]
	d3 = dif_list[-3] - dea_list[-3]
	d2 = dif_list[-2] - dea_list[-2]
	d1 = dif_list[-1] - dea_list[-1]
	
	#print(d4,d3,d2,d1)
	if dif_list[-4] < 0:
		if d4 < d3 and d3 < d2  and d2 >= d1:
			if price_list[-1] < price_list[-2] and price_list[-2] > price_list[-5]:
				print("[sell_dif_leave_dea] strategy hit")
				return 1, True
	return 0, False
	

'''
当dif和dea线连续都很接近的时候，不做买的操作，因为不明朗，看不清
'''
def buy_dif_leave_dea_too_small(dif_list, dea_list):
	d4 = abs(dif_list[-4] - dea_list[-4])
	d3 = abs(dif_list[-3] - dea_list[-3])
	d2 = abs(dif_list[-2] - dea_list[-2])
	d1 = abs(dif_list[-1] - dea_list[-1])
	
	distance = 0.006
	if d4 < distance and d3 < distance and d2 < distance and d1 < distance:
		print("[buy_dif_leave_dea_too_small] strategy hit")
		return 0, True
	return 1, False
	

'''
连续下跌了一个波段，并且hist是负数，并且柱子开始变短，
并且dif线的斜率不是往下，而是接近平，或者往上的时候，买入
'''
def buy_band_low_position(price_list, dif_list, dea_list, hist_list):
	if price_list[-1] >= price_list[-2] and price_list[-2] < price_list[-5]:
		#价格在波段低点
		if hist_list[-2] < -0.13 and hist_list[-1] - hist_list[-2] > 0.003:
			#判断dif的方向
			if dif_list[-1] - dif_list[-2] >= -0.02:
				print("[buy_band_low_position] strategy hit")
				return 1, True
	
	return 0, False


'''
在macd的红柱在上方突然上调的时候买入
'''
def buy_higher_red_hist(price_list, dif_list, dea_list, hist_list):
	if hist_list[-2] > 0:
		if hist_list[-2] < hist_list[-3] and hist_list[-1] > hist_list[-2]:
			if hist_list[-1] - hist_list[-2] > 0.02:
				if dea_list[-1] >= dea_list[-2]:
					print("[buy_higher_red_hist] strategy hit")
					return  1, True
	return 0, False
	
	
'''
判断周线级别的是否是在绝对的下降趋势中,是否是死叉趋势中
'''
def check_weekly_dead_cut(price_list, dif_list, dea_list, hist_list):
	if len(dif_list) <4 or len(dea_list) < 4 or len(hist_list) < 4:
		return 0, False
		
	d3 = dif_list[-3] - dea_list[-3]
	d2 = dif_list[-2] - dea_list[-2]
	d1 = dif_list[-1] - dea_list[-1]
	
	if d3 > d2 and d2 > d1 and abs(d1) < 0.15:
		if price_list[-1] < price_list[-3]:
			print("[check_weekly_dead_cut] strategy hit")
			return 1,True
	return 0, False
	
if __name__ == "__main__":
	dif_leave_dea([-5,-4,-3,-2,-4], [-2,-2,-2,-2,-2])
	
	
	
	
	
	
	
	