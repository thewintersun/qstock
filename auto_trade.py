from win32con import PAGE_READWRITE, MEM_COMMIT, MEM_RESERVE, MEM_RELEASE,\
    PROCESS_ALL_ACCESS
from commctrl import LVM_GETITEMTEXT, LVM_GETITEMCOUNT

import struct
import ctypes
import win32api
import win32gui
import time
import stock_op
import trader.trader

#"AUTO_BUY1", "量化金叉"
BUY_RULE = ["AUTO_BUY1"]

#"本地死叉"
SELL_RULE = ["量化死叉", "量化卖出1"]

buy_money_per_time = 20000.0

#当天是否禁止买入，在大盘死叉的时候可以设置
forbid_buy = True
forbid_buy = False


GetWindowThreadProcessId = ctypes.windll.user32.GetWindowThreadProcessId
VirtualAllocEx = ctypes.windll.kernel32.VirtualAllocEx
VirtualFreeEx = ctypes.windll.kernel32.VirtualFreeEx
OpenProcess = ctypes.windll.kernel32.OpenProcess
WriteProcessMemory = ctypes.windll.kernel32.WriteProcessMemory
ReadProcessMemory = ctypes.windll.kernel32.ReadProcessMemory
memcpy = ctypes.cdll.msvcrt.memcpy


def send_email(subject, body):
    key='lmiqlrkobjiwbhih'      #换成你的QQ邮箱SMTP的授权码(QQ邮箱设置里)
    EMAIL_ADDRESS='65361006@qq.com'      #换成你的邮箱地址
    EMAIL_PASSWORD=key

    import smtplib
    smtp=smtplib.SMTP('smtp.qq.com',25)

    import ssl
    context=ssl.create_default_context()
    sender=EMAIL_ADDRESS                                         #发件邮箱
    receiver=['65361006@qq.com','icosmore@foxmail.com'] 
                                          #收件邮箱
    from email.message import EmailMessage
    msg=EmailMessage()
    msg['subject']=subject       #邮件主题
    msg['From']=sender
    msg['To']=','.join(receiver)
    msg.set_content(body)         #邮件内容

    with smtplib.SMTP_SSL("smtp.qq.com",465,context=context) as smtp:
        smtp.login(EMAIL_ADDRESS,EMAIL_PASSWORD)
        smtp.send_message(msg)


def readListViewItems(hwnd, column_index=0):

    # Allocate virtual memory inside target process
    pid = ctypes.create_string_buffer(4)
    p_pid = ctypes.addressof(pid)
    GetWindowThreadProcessId(hwnd, p_pid) # process owning the given hwnd
    hProcHnd = OpenProcess(PROCESS_ALL_ACCESS, False, struct.unpack("i",pid)[0])
    pLVI = VirtualAllocEx(hProcHnd, 0, 4096, MEM_RESERVE|MEM_COMMIT, PAGE_READWRITE)
    pBuffer = VirtualAllocEx(hProcHnd, 0, 4096, MEM_RESERVE|MEM_COMMIT, PAGE_READWRITE)

    # Prepare an LVITEM record and write it to target process memory
    lvitem_str = struct.pack('iiiiiiiii', *[0,0,column_index,0,0,pBuffer,4096,0,0])
    lvitem_buffer = ctypes.create_string_buffer(lvitem_str)
    copied = ctypes.create_string_buffer(4)
    p_copied = ctypes.addressof(copied)
    WriteProcessMemory(hProcHnd, pLVI, ctypes.addressof(lvitem_buffer), ctypes.sizeof(lvitem_buffer), p_copied)

    # iterate items in the SysListView32 control
    num_items = win32gui.SendMessage(hwnd, LVM_GETITEMCOUNT)
    item_texts = []
    for item_index in range(num_items):
        win32gui.SendMessage(hwnd, LVM_GETITEMTEXT, item_index, pLVI)
        target_buff = ctypes.create_string_buffer(4096)
        ReadProcessMemory(hProcHnd, pBuffer, ctypes.addressof(target_buff), 4096, p_copied)
        item_texts.append(target_buff.value)

    VirtualFreeEx(hProcHnd, pBuffer, 0, MEM_RELEASE)
    VirtualFreeEx(hProcHnd, pLVI, 0, MEM_RELEASE)
    win32api.CloseHandle(hProcHnd)
    return item_texts



def get_all_info(hwnd):

    stock_name_list = []
    stock_id_list = []
    trick_time_list = []
    trick_price_list = []
    trick_type_list = []
    
    stock_info_list = []
    
    content = readListViewItems(hwnd, 0)
    for c in content:
        stock_name_list.append(c.decode('gb2312'))
        
    content = readListViewItems(hwnd, 1)
    for c in content:
        stock_id_list.append(c.decode('gb2312'))
        
    content = readListViewItems(hwnd, 2)
    for c in content:
        trick_time_list.append(c.decode('gb2312'))
        
    content = readListViewItems(hwnd, 3)
    for c in content:
        trick_price_list.append(c.decode('gb2312'))
        
    content = readListViewItems(hwnd, 5)
    for c in content:
        trick_type_list.append(c.decode('gb2312'))
    
    
    for i in range(len(stock_name_list)):
        stock_info_list.append((stock_name_list[i], stock_id_list[i], trick_time_list[i], trick_price_list[i], trick_type_list[i]))
    
    return stock_info_list
      
      
hwnd_title = {}
child_handles = []

def get_all_hwnd(hwnd, mouse):
    if (win32gui.IsWindow(hwnd)
            and win32gui.IsWindowEnabled(hwnd)
            and win32gui.IsWindowVisible(hwnd)):
        hwnd_title.update({hwnd: win32gui.GetWindowText(hwnd)})


def find_hwnd():
    win32gui.EnumWindows(get_all_hwnd, 0)
    for h, t in hwnd_title.items():
        if t :
            #print (h, t)
            if t.find("条件预警") != -1:
                return h
    return -1

def all_ok(hwnd, param):
    child_handles.append(hwnd)
    return True
    

def get_real_hld(parent_handle):
    inner_handles = win32gui.EnumChildWindows(parent_handle, all_ok, None)
    if len(child_handles)>0:
        return child_handles[0]
    return -1
    



def get_new_stock(old_stock_list, stock_list):
    old_dict = {}
    ret_list = []
    for s in old_stock_list:
        old_dict[s[0]] = 1
    
    for s in stock_list:
        if s[0] not in old_dict:
            ret_list.append(s)
    return ret_list
    
    
    
def resort_stock(stock_info_list):
    new_stock_info_list = []
    for s in stock_info_list:
        if s[4] in SELL_RULE:
            new_stock_info_list.append(s)
    for s in stock_info_list:
        if s[4] in BUY_RULE:
            new_stock_info_list.append(s)
    return new_stock_info_list
    
    
    
def run(run_type):
    hwnd = find_hwnd()
    if hwnd == -1:
        print("can not find 条件预警")
        return
    
    real_hld = get_real_hld(hwnd)
    if real_hld == -1:
        print("can not find 条件预警's sub windows")
        return
    

    if run_type == "real":
        # 实盘
        operator = stock_op.RealTrader()
        ret = operator.init()
        if ret != 0:
            print("初始化证券客户端失败")
            return 
    else:
        # 模拟
        operator = stock_op.MockTrader()
        ret = operator.init()
        if ret != 0:
            print("初始化模拟数据失败")
            return 
            
    old_stock_info_list = []

    i = 0
    max_trader_times = 100
    trade_times = 0
    while True:
        stock_info_list = get_all_info(real_hld)
        
        if len(old_stock_info_list) != len(stock_info_list):
            #有新的股出现
            new_stock_info = get_new_stock(old_stock_info_list, stock_info_list)
            
            #将sell的stock放到数组的前面
            new_stock_info = resort_stock(new_stock_info)
            
            # stock_name , stock_id, trick_time, trick_price, trick_type
            for s in new_stock_info:
                stock_number = (int((buy_money_per_time/float(s[3]))/100)) * 100
                stock_info = ([s[1], s[0], s[3], stock_number])
                stock_id = s[1]
                stock_name = s[0]
                price = float(s[3])
                number = int(stock_number)
                if (s[4] in BUY_RULE) and (forbid_buy is False):
                    print("buy:")
                    print(s)
                    
                    if trade_times > max_trader_times:
                        print("超过最大买入次数")
                        continue
                        
                    trade_times += 1
                    operator.buy_stock(stock_id, stock_name, price, number)

                if s[4] in SELL_RULE:
                    print("sell:")
                    print(s)
                    operator.sell_stock(stock_id)
                    
        old_stock_info_list = stock_info_list

        i += 1
        if i % 60 == 0:
            # 10 min
            operator.check_stop_loss()
        
        
        time.sleep(10)
        
            
if __name__ == "__main__":
    run("mock")
