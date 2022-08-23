import logging
import codecs
import easyquotation
import easytrader
import time
from easytrader import exceptions
from easytrader import refresh_strategies
from easytrader import grid_strategies

import traceback
import utils
import stock_config

logging.basicConfig(filename='logger.log', format='%(asctime)s  %(filename)s : %(levelname)s  %(message)s', level=logging.INFO)

    
class StockInfo():
    def __init__(self, sid:str, name:str, price:float, number:int):
        self.stock_id = sid
        self.stock_name = name
        self.cost_price = price
        self.number = number
        
        
class BaseTrader():
    def __init__(self):
        #123.22
        self.money_file="./money.txt"

        #stock_id, stock_name, price, number
        self.hold_stock_file="./holding_stock.txt"
        
        # 股票黑名单
        self.black_stock_file="./black_stock_file.txt"
        
        self.quotation = easyquotation.use('sina')
        
        # value 为1 代表前一天的股票， 2代表今天新买的股票
        self.holding_stock_id_dict = {}
        self.black_stock_dict = {}
        self.holding_stock_info_list = []
        
        self.remain_money = 0.0
        self.total_money = 0.0
        self.valid_money = 0.0
        
        self.hold_ratio=stock_config.HOLD_RATIO

    def load_black_stock_list(self):
        self.black_stock_dict={}
        with codecs.open(self.black_stock_file, 'r', 'utf-8') as fr:
            print("Black stock list:")
            for line in fr:
                print(line)
                self.black_stock_dict[line.strip()] = 1
    

    def get_buy_ask_price(self, stock_code):
        #获取5挡买卖数据
        
        try:
            data_dict = self.quotation.real(stock_code)
        except:
            logging.warning("[get_buy_ask_price] quotation.real network error {} use tdx price".format(stock_id))
            return -1, -1
            
        if data_dict:
            buy_list = (data_dict[stock_code]['bid1'], data_dict[stock_code]['bid2'], data_dict[stock_code]['bid3'], data_dict[stock_code]['bid4'], data_dict[stock_code]['bid5'])
            ask_list = (data_dict[stock_code]['ask1'], data_dict[stock_code]['ask2'], data_dict[stock_code]['ask3'], data_dict[stock_code]['ask4'], data_dict[stock_code]['ask5'])
            return buy_list, ask_list
            
        logging.warning("[NetworkExcept] Can not get stock {} buy_ask_price".format(stock_id))
        return -1, -1
        
    def buy_stock(self, stock_id:str, stock_name:str, price:float, number:int):
        pass
        
    def sell_stock(self, stock_id,  price):
        pass
        
    def syc_data(self):
        #同步数据，模拟盘和本地文件同步， 实盘和券商结果同步
        pass


    def _get_zf(self, stock_id):
        # 获取一个股价的涨幅
        try:
            data_dict = self.quotation.real(stock_id)
        except:
            logging.warning("[get_zf] quotation.real network error {}".format(stock_id))
            return -1
        
        if data_dict:
            now_price = data_dict[stock_id]['now']
            last_close = data_dict[stock_id]['close'] 
            zf = (now_price - last_close)/last_close
            
            if zf < -0.05:
                logging.warning("[GET_ZF] Impossibel! zf < -5% but selected this stock {}".format(stock_id))
                return -1
            return zf
        logging.warning("[NetworkExcept] Can not get stock {} realtime info".format(stock_id))
        return -1
        

class MockTrader(BaseTrader):
    def __init__(self):
        super().__init__()
        #123.22
        self.money_file="./mock/money.txt"
        
        self.total_money_file="./mock/total_money.txt"

        #stock_id, stock_name, price, number
        self.hold_stock_file="./mock/holding_stock.txt"
        
        # 股票黑名单
        self.black_stock_file="./mock/black_stock_file.txt"

        
    def init(self):
        self.load_black_stock_list()
        self.syc_data()
        return 0
        
    def syc_data(self):
        #同步数据，模拟盘和本地文件同步， 实盘和券商结果同步
        self.holding_stock_id_dict = {}
        self.holding_stock_info_list = []
        with codecs.open(self.hold_stock_file, 'r', 'utf-8') as fr:
            for line in fr:
                line_arr = line.strip().split('\t')
                self.holding_stock_id_dict[line_arr[0]] = 1
                
                stock_info = StockInfo(line_arr[0], line_arr[1], float(line_arr[2]), int(line_arr[3]))
                self.holding_stock_info_list.append(stock_info)
                
        with codecs.open(self.money_file, 'r','utf-8') as fr:
            for line in fr:
                self.remain_money = float(line.strip())
                break
        with codecs.open(self.total_money_file, 'r','utf-8') as fr:
            for line in fr:
                self.total_money = float(line.strip())
                break

        buyed_money = self.total_money - self.remain_money
        self.valid_money = min((self.total_money * self.hold_ratio - buyed_money), self.remain_money)
        

    def write_data(self):
        #将数据写入到文件，应该只有模拟盘才有，实盘直接交易成功，就在券商的数据里了。
        with codecs.open(self.money_file, 'w','utf-8') as fw:
            fw.write(str(self.remain_money))
        
        with codecs.open(self.hold_stock_file, 'w','utf-8') as fw:
            for stock_info in self.holding_stock_info_list:
                fw.write("{}\t{}\t{}\t{}\n".format(stock_info.stock_id, stock_info.stock_name, stock_info.cost_price, stock_info.number))


    def buy_stock(self, stock_id:str, stock_name:str, price:float, number:int):
        if stock_id in self.black_stock_dict:
            logging.info("[black_list] stock in black list {}".format(stock_id))
            return
            
        if stock_id in self.holding_stock_id_dict:
            logging.info("[!!!] stock already in holding stock {}".format(stock_id))
            return
            
        if number == 0:
            return
            
        zf = self._get_zf(stock_id)
        if zf == -1:
            return
            
        if zf > 0.05:
            logging.info("[!!!] stock up bigger than 5%, not buy {} {}".format(stock_id, price))
            return
                  

        buy_list, ask_list = self.get_buy_ask_price(stock_id)
        if buy_list == -1:
            # 加 0.05，保证成交
            price = price + 0.05
        else:
            price = ask_list[1]
        
        waste_money = price * number
        if waste_money < self.valid_money:
            logging.info("[buy]\t{}\t{}\t{}\t{}".format(stock_id, stock_name, price, number))
            self.remain_money -= waste_money
            self.valid_money -= waste_money
            
            #佣金 万一
            self.remain_money -= waste_money * 0.0001
            self.valid_money -= waste_money * 0.0001
            
            self.holding_stock_id_dict[stock_id] = 2
            
            stock_info = StockInfo(stock_id, stock_name, price, number)
            self.holding_stock_info_list.append(stock_info)
        else:
            logging.info("[!!!] No enough money buy stock: {}\t{}\t{}\t{}\t{}\t{}".format(self.remain_money, waste_money, stock_id, stock_name, price, number))
            return
        self.write_data()


    # [stock_id, stock_name, price, number]
    def sell_stock(self, stock_id, price):
        buy_list, ask_list = self.get_buy_ask_price(stock_id)
        if buy_list == -1:
            price = price - 0.05
        else:
            price = buy_list[1]
        
        if stock_id in self.holding_stock_id_dict:
            if self.holding_stock_id_dict[stock_id] == 2:
                logging.info("[SELL_ERROR] can not sell stock buyed today. {}".format(stock_id))
                return
                
            for i in range(len(self.holding_stock_info_list)):
                stock_info = self.holding_stock_info_list[i]
                if stock_info.stock_id == stock_id:
                    number = stock_info.number
                    
                    get_money = price * number
                    self.remain_money += get_money
                    self.valid_money += get_money
                    
                    #印花税加佣金
                    self.remain_money -= get_money * 0.0011
                    self.valid_money -= get_money * 0.0011
            

                    logging.info("[sell]\t{}\t{}\t{}\t{}".format(stock_id, stock_info.stock_name, price, number))
                    
                    profit = get_money - number * stock_info.cost_price
                    logging.info("[sell_profit]\t{}\t{}\t{}".format(stock_id, stock_info.stock_name, profit))

                    self.holding_stock_info_list.pop(i)
                    self.holding_stock_id_dict.pop(stock_id)
                    break
            self.write_data()
        else:
            logging.warning("[!!!][SELL_ERROR] Not find sell stock in holding stock list. {}".format(stock_id))
            
        
    def check_stop_loss(self):
        #读取成本价
        
        for stock_info in self.holding_stock_info_list:
            stock_id, stock_name, cost_price = stock_info.stock_id, stock_info.stock_name, stock_info.cost_price
            if self.holding_stock_id_dict[stock_id] == 2:
                continue
            
            try:
                data_dict = self.quotation.real(stock_id)
            except:
                logging.warning("[REAL][stop_loss] network error {}".format(stock_id))
                continue
            
            if data_dict:
                #print(data_dict)
                now_price = data_dict[stock_id]['now']
                
                zf = (float(now_price - cost_price))/ cost_price
                if zf < -0.2:
                    logging.warning("[EXCEPT] realtime price un-normal stock:{} now_price:{}  cost_price:{}".format(stock_name, now_price, cost_price))
                    continue
            
                if zf < -0.05:
                    # force sell
                    logging.info("[stop_loss] {} {} {}".format(stock_name, cost_price, now_price))
                    self.sell_stock(stock_id, now_price)
            else:
                logging.warning("[quot_error] Get stock realtime info error {}".format(stock_id))



'''------------------------------------------------实盘Trader--------------------------------------------------------'''
class RealTrader(BaseTrader):
    def __init__(self):
        super().__init__()
        #123.22
        self.money_file="./real/money.txt"

        #stock_id, stock_name, price, number
        self.hold_stock_file="./real/holding_stock.txt"
        
        # 股票黑名单
        self.black_stock_file="./real/black_stock_file.txt"
        
        self.chengbenjia_key = "参考成本价"
        
    def init(self):
        client_type = stock_config.CLIENT_TYPE
        refresh_index = 4
        
        if client_type == 'gj_client':
            xiadan_path = r'C:\国金证券同花顺独立下单\xiadan.exe'
            refresh_index = 4
        elif client_type == 'ht_client':
            xiadan_path = r'C:\htzqzyb3\xiadan.exe'
            self.chengbenjia_key = "成本价"
            refresh_index = 5
            
        try:
            self.user = easytrader.use(client_type)
            self.user.connect(xiadan_path)
        except:
            print("初始化证券客户端失败")
            traceback.print_exc()
            return -1

        self.load_black_stock_list()
        
        self.user.refresh_strategy = refresh_strategies.Toolbar(refresh_btn_index=refresh_index)
        self.user.grid_strategy = grid_strategies.Xls
        self.user.enable_type_keys_for_editor()
        self.user.grid_strategy_instance.tmp_folder = 'C:\\custom_folder'


        ret = self.syc_data()
        if ret != 0:
            return -2

        self.write_data()
        
        return 0
    
    
    def update_remain_money(self):
        #获取资金情况
        try:
            balance = self.user.balance
            print(balance)
            if balance:
                self.remain_money = balance['可用金额']
                self.total_money = balance['总资产']
                
                buyed_money = self.total_money - self.remain_money
                self.valid_money = min((self.total_money * self.hold_ratio - buyed_money), self.remain_money)
                
                print("账户余额: {} 账户总额: {} 仓位限制:{} 限制后有效余额:{}".format(self.remain_money, self.total_money, self.hold_ratio, self.valid_money))
                logging.info("账户余额: {} 账户总额: {} 仓位限制:{} 限制后有效余额:{}".format(self.remain_money, self.total_money, self.hold_ratio, self.valid_money))
            else:
                logging.warning("[REAL][BALANCE] Get remain money error. ")
                return -1
        except:
            traceback.print_exc()
            return -1
        return 0
        
            
    #同步数据，模拟盘和本地文件同步， 实盘和券商结果同步
    def syc_data(self):
        print("开始同步实盘持仓数据.....")
        logging.info("开始同步实盘持仓数据.....")
        
        ret = self.update_remain_money()
        if ret == -1:
            return ret
        
        time.sleep(1)
        #获取持仓股
        try:
            position_data = self.user.position
        except:
            traceback.print_exc()
            return -1
        
        print(position_data)
        print("一共有{}个持仓股".format(len(position_data)))
        if position_data:
            self.holding_stock_id_dict = {}
            self.holding_stock_info_list = []
            
            for stock in position_data:
                stock_id = stock["证券代码"]
                stock_name = stock["证券名称"]
                stock_num = stock["股票余额"]
                cost_price = stock[self.chengbenjia_key]
                
                if stock_id.startswith('="'):
                    stock_id = stock_id.replace('="', '').replace('"', '')
                
                print("{} {} {} {}".format(stock_id, stock_name, float(cost_price), int(stock_num)))
                
                logging.info("{} {} {} {}".format(stock_id, stock_name, float(cost_price), int(stock_num)))
                
                stock_info = StockInfo(stock_id, stock_name, float(cost_price), int(stock_num))
                
                self.holding_stock_id_dict[stock_id] = 1
                self.holding_stock_info_list.append(stock_info)
        else:
            logging.warning("[REAL][position] No holding stock. ")
            
            
        return 0


    def write_data(self):
        #将数据写入到文件，应该只有模拟盘才有，实盘只是做下记录，数据获取在券商的数据里
        with codecs.open(self.money_file, 'w','utf-8') as fw:
            fw.write(str(self.remain_money))
        
        with codecs.open(self.hold_stock_file, 'w','utf-8') as fw:
            for stock_info in self.holding_stock_info_list:
                fw.write("{}\t{}\t{}\t{}\n".format(stock_info.stock_id, stock_info.stock_name, stock_info.cost_price, stock_info.number))


    def buy_stock(self, stock_id:str, stock_name:str, price:float, number:int):
        if stock_id in self.black_stock_dict:
            logging.info("[REAL][black_list] stock in black list {}".format(stock_id))
            return
            
        if stock_id in self.holding_stock_id_dict:
            logging.info("[REAL][!!!] stock already in holding stock {}".format(stock_id))
            return
            
        if number == 0:
            logging.info("[REAL][!!!] stock buy number is 0 {}".format(stock_id))
            return
            
        zf = self._get_zf(stock_id)
        if zf == -1:
            return
            
        if zf > 0.05:
            logging.info("[REAL][!!!] stock up bigger than 5%, not buy {} {}".format(stock_id, price))
            return
                  
        buy_list, ask_list = self.get_buy_ask_price(stock_id)

        if buy_list == -1:
            # 加 1%，保证成交
            price = round(price * 1.01, 2)
        else:
            price = ask_list[4]
            

        price = round(price, 2)
        if price == int(price):
            price = int(price)
        
        waste_money = price * number

        if waste_money < self.valid_money:
            #真实操作，买入股票
            print("[REAL][buy]\t{}\t{}\t{}\t{}".format(stock_id, stock_name, price, number))
            try:
                ret = self.user.buy(stock_id, price=price, amount=number)
                if ('message' in ret) and (ret['message'] == 'success'):
                    logging.info("[REAL][BUY] Buy stock success\t{}\t{}\t{}\t{}".format(stock_id, stock_name, price, number))
                    utils.send_email("股票:实盘买入:{} {}股".format(stock_name, number), "实盘买入:{} {}股,参考价格{}".format(stock_name, number, price))
                    
                elif ('entrust_no' in ret):
                    print("[REAL][BUY][entrust] entrust stock, entrust no is {}".format(ret['entrust_no']))
                    logging.info("[REAL][BUY] entrust stock, entrust no is {}".format(ret['entrust_no']))
                    
                    utils.send_email("股票:实盘委托:{} {}股".format(stock_name, number), "实盘买入:{} {}股,参考价格{}".format(stock_name, number, price))
                    
                else:
                    print("[REAL][BUY] Error, buy stock failed. {} {} {}".format(stock_id, price, number))
                    return -1
            except:
                print("交易失败")
                logging.warning("[REAL][BUY][!!!] invoke buy interface failed. {} {} {}".format(stock_id, price, number))
                traceback.print_exc()
                
                return -1

            self.holding_stock_id_dict[stock_id] = 2
            stock_info = StockInfo(stock_id, stock_name, price, number)
            self.holding_stock_info_list.append(stock_info)
            
            ret = self.update_remain_money()
            if ret == -1:
                print("[REAL] update remain money failed.")
                logging.warning("[REAL] update remain money failed.")
                self.remain_money -= waste_money
                self.valid_money -= waste_money

        else:
            logging.info("[REAL][!!!] No enough money buy stock: {}\t{}\t{}\t{}\t{}\t{}".format(self.remain_money, waste_money, stock_id, stock_name, price, number))
            return
        
        self.write_data()


    # [stock_id, stock_name, price, number]
    def sell_stock(self, stock_id, price):
        ret = -1
        buy_list, ask_list = self.get_buy_ask_price(stock_id)
        if buy_list == -1:
            # 小于1%，保证卖掉
            price = round(price * 0.99, 2)
        else:
            price = buy_list[4]
        
        if stock_id in self.holding_stock_id_dict:
            if self.holding_stock_id_dict[stock_id] == 2:
                logging.info("[REAL][SELL_ERROR] can not sell stock buyed today. {}".format(stock_id))
                return
                
            for i in range(len(self.holding_stock_info_list)):
                stock_info = self.holding_stock_info_list[i]
                if stock_info.stock_id == stock_id:
                    number = stock_info.number
                    try:
                        ret = self.user.sell(stock_id, price=price, amount=number)
                    except:
                        traceback.print_exc()
                        return -1
                        
                    print("[REAL][SELL] ret: ")
                    print(ret)
                    print(type(ret))

                    logging.info("[REAL][SELL]\t{}\t{}\t{}\t{}".format(stock_id, stock_name, price, number))
                    utils.send_email("股票:实盘卖出:{} {}股".format(stock_name, number), "实盘卖出:{} {}股,参考价格{}".format(stock_name, number, price))

                    self.holding_stock_info_list.pop(i)
                    self.holding_stock_id_dict.pop(stock_id)
                    
                    ret = self.update_remain_money()
                    if ret == -1:
                        print("[REAL] update remain money failed.")
                        logging.warning("[REAL] update remain money failed.")
                        get_money = price * number
                        self.remain_money += get_money
                        self.valid_money += get_money
                    break
            self.write_data()
        else:
            logging.warning("[REAL][SELL_ERROR] Not find sell stock in holding stock list. {}".format(stock_id))
        return 0
        
        
    def check_stop_loss(self):
        #读取成本价
        
        for stock_info in self.holding_stock_info_list:
            stock_id, stock_name, cost_price = stock_info.stock_id, stock_info.stock_name, stock_info.cost_price
            
            #如果今天买的，今天不能卖，跳过
            if self.holding_stock_id_dict[stock_id] == 2:
                continue
                
            try:
                data_dict = self.quotation.real(stock_id)
            except:
                logging.warning("[REAL][stop_loss] network error {}".format(stock_id))
                continue
                
            if data_dict:
                now_price = data_dict[stock_id]['now']
                
                zf = (float(now_price - cost_price))/ cost_price
                if zf > 0.25 or zf < -0.2:
                    logging.warning("[REAL][EXCEPT] realtime price un-normal stock:{} now_price:{}  cost_price:{}".format(stock_name, now_price, cost_price))
                    continue
            
                if zf < -0.05:
                    # force sell
                    logging.info("[REAL][stop_loss] {} {} {}".format(stock_name, cost_price, now_price))
                    self.sell_stock(stock_id, now_price)
            else:
                logging.warning("[REAL][quot_error] Get stock realtime info error {}".format(stock_id))




if __name__ == "__main__":
    user = RealTrader()
    ret = user.init()
    print(ret)
    ret = user.sell_stock( "002422", 12.0)
    print(ret)