import tushare as ts
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import talib

ts.set_token('46dc6393e4bee0a19b34625a8292d258827f2d4c62777e11cd5f0998')
pro = ts.pro_api()

import tushare as ts
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import talib

df=ts.get_k_data('600600')
close = [float(x) for x in df['close']]
df['RSI']=talib.RSI(np.array(close), timeperiod=12)     #RSI的天数一般是6、12、24
df['MOM']=talib.MOM(np.array(close), timeperiod=5)
df.tail(12)


data = ts.get_hist_data('000001', start="2020-08-02")

close_1 = np.array(data['close'])

close = np.flipud(close_1)
print(len(close))

dif, dea, macd = talib.MACD(close,fastperiod=12,slowperiod=26,signalperiod=9)

macd_1 = np.zeros(len(macd))
macd_0 = np.zeros(len(macd))

for i in range(len(macd)):
    if macd[i] >= 0:
        macd_1[i] = macd[i]
    else:
        macd_0[i] = macd[i]

fig = plt.figure(figsize=[36,5])
plt.plot(dif,label='dif')
plt.plot(dea,color='yellow',label='dea')
#plt.bar(range(len(macd)),macd_1*2,color='red',label='Red_Bar')
#plt.bar(range(len(macd)),macd_0*2,color='green',label='Green_Bar')
plt.legend()
plt.hlines(0,0,200) 
plt.show()