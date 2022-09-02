# qstock


## 依赖软件

windows版本的通达信金融终端

通达信对应的选股公式

python， 如果通达信是32位的，python的版本也要装32位的。

easytrader， easytrader的安装过程中，可能还要装微软的build tools， 可以选择那个full的exe，可能需要4G的空间。

https://download.microsoft.com/download/5/f/7/5f7acaeb-8363-451f-9425-68a90f98b238/visualcppbuildtools_full.exe


券商的windows客户端


ocr的软件的安装，装64位的。（不管通达信的版本）
https://www.jianshu.com/p/93ab58dea50f


pip install easyquotation
pip install pypiwin32
pip install easytrader

下载talib
https://download.lfd.uci.edu/pythonlibs/archived/TA_Lib-0.4.24-cp310-cp310-win32.whl
然后pip安装


## 交易客户端需要修改的地方

1. 系统设置 > 交易设置: 默认买入价格/买入数量/卖出价格/卖出数量 都设置为 空

2. 该项功能相关设定在“系统” > “系统设置” > “快速交易” > “自动弹出窗口停留时间(秒)”，最低设定为1秒。

3. 参考下这个修改代码，不过代码已经修改了。 https://github.com/shidenggui/easytrader/blob/master/docs/help.md

4. 修改easytrader的代码里的clienttrader.py文件，将_submit_trade函数里的click，修改成click_input; 前后是否延长sleep的时间，根据实际情况定。

