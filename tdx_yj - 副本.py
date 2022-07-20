from win32con import PAGE_READWRITE, MEM_COMMIT, MEM_RESERVE, MEM_RELEASE,\
    PROCESS_ALL_ACCESS
from commctrl import LVM_GETITEMTEXT, LVM_GETITEMCOUNT

import struct
import ctypes
import win32api
import win32gui
import time


GetWindowThreadProcessId = ctypes.windll.user32.GetWindowThreadProcessId
VirtualAllocEx = ctypes.windll.kernel32.VirtualAllocEx
VirtualFreeEx = ctypes.windll.kernel32.VirtualFreeEx
OpenProcess = ctypes.windll.kernel32.OpenProcess
WriteProcessMemory = ctypes.windll.kernel32.WriteProcessMemory
ReadProcessMemory = ctypes.windll.kernel32.ReadProcessMemory
memcpy = ctypes.cdll.msvcrt.memcpy


def send_email(subject, body):
    key=''      #换成你的QQ邮箱SMTP的授权码(QQ邮箱设置里)
    EMAIL_ADDRESS='@qq.com'      #换成你的邮箱地址
    EMAIL_PASSWORD=key

    import smtplib
    smtp=smtplib.SMTP('smtp.qq.com',25)

    import ssl
    context=ssl.create_default_context()
    sender=EMAIL_ADDRESS                                         #发件邮箱
    receiver=['@qq.com','@foxmail.com', '@airchinacargo.com', '@126.com'] 
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
    
    '''
    for i in range(len(stock_name_list)):
        print(stock_name_list[i], stock_id_list[i], trick_time_list[i], trick_price_list[i], trick_type_list[i])
    '''
    return stock_name_list, trick_type_list
      
      
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
    
def find_diff_send_mail(old_stock_name_list, stock_name_list, trick_type_list):
    subject = ""
    body = ""
    for i in range(len(stock_name_list)):
        name = stock_name_list[i]
        tag = ""
        if name not in old_stock_name_list:
            subject += name + "|"
            tag = " *"
        body += stock_name_list[i] + '\t' + trick_type_list[i] + tag  + '\n'
    
    print("subject: {} \n body: {}".format(subject, body))
    send_email(subject, body)
    
    
def run():
    hwnd = find_hwnd()
    if hwnd == -1:
        print("can not find 条件预警")
        return
    
    real_hld = get_real_hld(hwnd)
    if real_hld == -1:
        print("can not find 条件预警's sub windows")
        return
    
    old_stock_name_list = []
    old_trick_type_list = []
    
    while True:
        stock_name_list, trick_type_list = get_all_info(real_hld)
        
        if len(old_stock_name_list) != len(stock_name_list):
            #有新的股出现
            find_diff_send_mail(old_stock_name_list, stock_name_list, trick_type_list)
            old_stock_name_list = stock_name_list
            old_trick_type_list = trick_type_list
        time.sleep(10)
            
if __name__ == "__main__":
    run()
