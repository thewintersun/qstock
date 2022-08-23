import codecs
import easyquotation


#stock_id, stock_name, price, number
hold_stock_file="./mock/holding_stock.txt"

money_file="./mock/money.txt"

quotation = easyquotation.use('sina')


def get_now_price( stock_id):
    data_dict = quotation.real(stock_id)
    
    if data_dict:
        now_price = data_dict[stock_id]['now']
        return now_price
    print("error")
    return -1
        
        
def calc_total():
    name_price_dict = {}
    total_money = 0
            
    with codecs.open(hold_stock_file, 'r', 'utf-8') as fr:
        for line in fr:
            line_arr = line.strip().split('\t')
            sid, number  = line_arr[0], line_arr[3]
            price = get_now_price(sid)
            total_money += price * int(number)
            
    with codecs.open(money_file, 'r', 'utf-8') as fr:
        for line in fr:
            total_money += float(line.strip())
            
    print(total_money)
    
    
    
if __name__ == "__main__":
    calc_total()