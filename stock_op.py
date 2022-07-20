import logging
import codecs
import easyquotation
import easytrader
import time
from easytrader import exceptions
import traceback


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

    def load_black_stock_list(self):
        self.black_stock_dict={}
        with codecs.open(self.black_stock_file, 'r', 'utf-8') as fr:
            print("Black stock list:")
            for line in fr:
                print(line)
                self.black_stock_dict[line.strip()] = 1
    

    def get_buy_ask_price(self, stock_code):
        #获取5挡买卖数据

        data_dict = self.quotation.real(stock_code)
        if data_dict:
            buy_list = (data_dict[stock_code]['bid1'], data_dict[stock_code]['bid2'], data_dict[stock_code]['bid3'], data_dict[stock_code]['bid4'], data_dict[stock_code]['bid5'])
            ask_list = (data_dict[stock_code]['ask1'], data_dict[stock_code]['ask2'], data_dict[stock_code]['ask3'], data_dict[stock_code]['ask4'], data_dict[stock_code]['ask5'])
            return buy_list, ask_list
            
        logging.warning("[NetworkExcept] Can not get stock {} buy_ask_price".format(stock_id))
        return -1, -1
        
    def buy_stock(self, stock_id, stock_name, price, number):
        pass
        
    def sell_stock(self, stock_id, stock_name, price, number):
        pass
        
    def syc_data(self):
        #同步数据，模拟盘和本地文件同步， 实盘和券商结果同步
        pass


    def _get_zf(self, stock_id):
        # 获取一个股价的涨幅
        data_dict = self.quotation.real(stock_id)
        
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
    

    def write_data(self):
        #将数据写入到文件，应该只有模拟盘才有，实盘直接交易成功，就在券商的数据里了。
        with codecs.open(self.money_file, 'w','utf-8') as fw:
            fw.write(str(self.remain_money))
        
        with codecs.open(self.hold_stock_file, 'w','utf-8') as fw:
            for stock_info in self.holding_stock_info_list:
                fw.write("{}\t{}\t{}\t{}\n".format(stock_info.stock_id, stock_info.stock_name, stock_info.cost_price, stock_info.number))


    def buy_stock(self, stock_id, stock_name, price, number):
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
            return
            
        price = ask_list[1]
        waste_money = price * number
        if waste_money < self.remain_money:
            logging.info("[buy]\t{}\t{}\t{}\t{}".format(stock_id, stock_name, price, number))
            self.remain_money = self.remain_money - waste_money
            self.holding_stock_id_dict[stock_id] = 2
            
            stock_info = StockInfo(stock_id, stock_name, price, number)
            self.holding_stock_info_list.append(stock_info)
        else:
            logging.info("[!!!] No enough money buy stock: {}\t{}\t{}\t{}\t{}\t{}".format(self.remain_money, waste_money, stock_id, stock_name, price, number))
            return
        self.write_data()


    # [stock_id, stock_name, price, number]
    def sell_stock(self, stock_id):
        buy_list, ask_list = self.get_buy_ask_price(stock_id)
        if buy_list == -1:
            return
        
        if stock_id in self.holding_stock_id_dict:
            if self.holding_stock_id_dict[stock_id] == 2:
                logging.info("[SELL_ERROR] can not sell stock buyed today. {}".format(stock_id))
                return
                
            for i in range(len(self.holding_stock_info_list)):
                stock_info = self.holding_stock_info_list[i]
                if stock_info.stock_id == stock_id:
                    number = stock_info.number
                    price = buy_list[1]
                    get_money = price * number
                    self.remain_money += get_money

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
            data_dict = self.quotation.real(stock_id)
            
            if data_dict:
                print(data_dict)
                now_price = data_dict[stock_id]['now']
                
                zf = (float(now_price - cost_price))/ cost_price
                if zf > 0.25 or zf < -0.2:
                    logging.warning("[EXCEPT] realtime price un-normal stock:{} now_price:{}  cost_price:{}".format(stock_name, now_price, cost_price))
                    continue
            
                if zf < -0.05:
                    # force sell
                    logging.info("[stop_loss] {} {} {}".format(stock_name, cost_price, now_price))
                    self.sell_stock(stock_id)
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
        
        
    def init(self):
        try:
            self.user = easytrader.use('gj_client')
            self.user.connect(r'C:\国金证券同花顺独立下单\xiadan.exe')
        except:
            print("初始化证券客户端失败")
            traceback.print_exc()
            return -1


        self.load_black_stock_list()
        ret = self.syc_data()
        if ret != 0:
            return ret
        return 0
    
    
    def update_remain_money(self):
        #获取资金情况
        balance = self.user.balance
        print(balance)
        if balance:
            self.remain_money = balance['可用金额']
            print("账户余额: {}".format(self.remain_money))
        else:
            logging.warning("[REAL][BALANCE] Get remain money error. ")
            return -1
            
            
    #同步数据，模拟盘和本地文件同步， 实盘和券商结果同步
    def syc_data(self):
        print("开始同步实盘持仓数据.....")
        
        ret = self.update_remain_money()
        if ret == -1:
            return ret
        
        time.sleep(1)
        #获取持仓股
        position_data = self.user.position
        print(position_data)
        print("一共有{}个持仓股".format(len(position_data)))
        if position_data:
            self.holding_stock_id_dict = {}
            self.holding_stock_info_list = []
            
            for stock in position_data:
                stock_id = stock["证券代码"]
                stock_name = stock["证券名称"]
                stock_num = stock["股票余额"]
                cost_price = stock["参考成本价"]
                
                if stock_id.startswith('="'):
                    stock_id = stock_id.replace('="', '').replace('"', '')
                
                print("{} {} {} {}".format(stock_id, stock_name, float(cost_price), int(stock_num)))
                stock_info = StockInfo(stock_id, stock_name, float(cost_price), int(stock_num))
                
                self.holding_stock_id_dict[stock_id] = 1
                self.holding_stock_info_list.append(stock_info)
        else:
            logging.warning("[REAL][position] No holding stock. ")
            return -1
            
        return 0

    def write_data(self):
        #将数据写入到文件，应该只有模拟盘才有，实盘只是做下记录，数据获取在券商的数据里
        with codecs.open(self.money_file, 'w','utf-8') as fw:
            fw.write(str(self.remain_money))
        
        with codecs.open(self.hold_stock_file, 'w','utf-8') as fw:
            for stock_info in self.holding_stock_info_list:
                fw.write("{}\t{}\t{}\t{}\n".format(stock_info.stock_id, stock_info.stock_name, stock_info.cost_price, stock_info.number))


    def buy_stock(self, stock_id, stock_name, price, number):
        if stock_id in self.black_stock_dict:
            logging.info("[REAL][black_list] stock in black list {}".format(stock_id))
            return
            
        if stock_id in self.holding_stock_id_dict:
            logging.info("[REAL][!!!] stock already in holding stock {}".format(stock_id))
            return
            
        if number == 0:
            return
            
        zf = self._get_zf(stock_id)
        if zf == -1:
            return
            
        if zf > 0.05:
            logging.info("[REAL][!!!] stock up bigger than 5%, not buy {} {}".format(stock_id, price))
            return
                  
        buy_list, ask_list = self.get_buy_ask_price(stock_id)
        if buy_list == -1:
            return
            
        price = ask_list[4]
        waste_money = price * number
        if waste_money < self.remain_money:
            #真实操作，买入股票
            print("[REAL][buy]\t{}\t{}\t{}\t{}".format(stock_id, stock_name, price, number))
            try:
                ret = self.user.buy(stock_id, price=price, amount=number)
                if ('message' in ret) and (ret['message'] == 'success'):
                    logging.info("[REAL][BUY] Buy stock success\t{}\t{}\t{}\t{}".format(stock_id, stock_name, price, number))
                elif ('entrust_no' in ret):
                    print("[REAL][BUY][entrust] entrust stock, entrust no is {}".format(ret['entrust_no']))
                    logging.info("[REAL][BUY] entrust stock, entrust no is {}".format(ret['entrust_no']))
                else:
                    print("[REAL][BUY] Error, buy stock failed. {} {} {}".format(stock_id, price, number))
                    return -1
            except:
                print("交易失败")
                print(ret)
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
                self.remain_money = self.remain_money - waste_money

        else:
            logging.info("[REAL][!!!] No enough money buy stock: {}\t{}\t{}\t{}\t{}\t{}".format(self.remain_money, waste_money, stock_id, stock_name, price, number))
            return
        
        self.write_data()


    # [stock_id, stock_name, price, number]
    def sell_stock(self, stock_id):
        ret = -1
        buy_list, ask_list = self.get_buy_ask_price(stock_id)
        if buy_list == -1:
            return
        
        if stock_id in self.holding_stock_id_dict:
            if self.holding_stock_id_dict[stock_id] == 2:
                logging.info("[REAL][SELL_ERROR] can not sell stock buyed today. {}".format(stock_id))
                return
                
            for i in range(len(self.holding_stock_info_list)):
                stock_info = self.holding_stock_info_list[i]
                if stock_info.stock_id == stock_id:
                    number = stock_info.number
                    price = buy_list[4]
                    try:
                        ret = self.user.sell(stock_id, price=price, amount=number)
                    except:
                        traceback.print_exc()
                        return -1
                        
                    print("[REAL][SELL] ret: ")
                    print(ret)
                    print(type(ret))

                    logging.info("[REAL][SELL]\t{}\t{}\t{}\t{}".format(stock_id, stock_name, price, number))

                    self.holding_stock_info_list.pop(i)
                    self.holding_stock_id_dict.pop(stock_id)
                    
                    ret = self.update_remain_money()
                    if ret == -1:
                        print("[REAL] update remain money failed.")
                        logging.warning("[REAL] update remain money failed.")
                        get_money = price * number
                        self.remain_money += get_money
                    break
            self.write_data()
        else:
            logging.warning("[REAL][SELL_ERROR] Not find sell stock in holding stock list. {}".format(stock_id))
        
        
        
    def check_stop_loss(self):
        #读取成本价
        
        for stock_info in self.holding_stock_info_list:
            stock_id, stock_name, cost_price = stock_info.stock_id, stock_info.stock_name, stock_info.cost_price
            data_dict = self.quotation.real(stock_id)
            
            if data_dict:
                print(data_dict)
                now_price = data_dict[stock_id]['now']
                
                zf = (float(now_price - cost_price))/ cost_price
                if zf > 0.25 or zf < -0.2:
                    logging.warning("[REAL][EXCEPT] realtime price un-normal stock:{} now_price:{}  cost_price:{}".format(stock_name, now_price, cost_price))
                    continue
            
                if zf < -0.05:
                    # force sell
                    logging.info("[REAL][stop_loss] {} {} {}".format(stock_name, cost_price, now_price))
                    self.sell_stock(stock_id)
            else:
                logging.warning("[REAL][quot_error] Get stock realtime info error {}".format(stock_id))




if __name__ == "__main__":
    user = RealTrader()
    ret = user.init()
    print(ret)
    ret = user.sell_stock( "002422")
    print(ret)