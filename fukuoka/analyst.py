#coding=utf-8
#!/usr/bin/python

#图形化输出价格波动数据统计结果
import matplotlib.pyplot as plt
import os
import sys
import time
import xlrd
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
import findChance
import math




#***************************************************************
if __name__ == '__main__':

     path = 'priceData/'
     fig = plt.figure()
     fileOfSymbol=[]
     xvalue=[]
     yvalue=[]
     yvalue1=[]
     data = xlrd.open_workbook("priceData/1.xls")
     table = data.sheets()[0]
     yvalue1 += table.col_values(2)
     yvalue += table.col_values(3)
     xvalue += table.col_values(1)



     xs = [datetime.strptime(d, '%Y-%m-%d %H:%M:%S') for d in xvalue]
     ys=yvalue
     ys1=yvalue1
     fig = plt.figure()
     fig.suptitle("demo", fontsize=20)



     plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%y-%m-%d %H')) #x轴上的label格式为"年-月-日",其中年取后两位
     plt.gca().xaxis.set_major_locator(mdates.DayLocator())
     plt.xticks(pd.date_range(xs[0],xs[-1]))



     # Plot
     #plt.plot(xs, ys)
     #bianSell_huobiBuy
     plt.plot(xs, ys, linewidth = 1, label = "demo", color='green',marker=".")
     #huobiSell_bianBuy
     plt.plot(xs, ys1, linewidth = 1, label = "demo", color='red',marker=".")

     plt.axhline(0,linestyle='-',linewidth=1, color='black')
     plt.gcf().autofmt_xdate()  # 自动旋转日期标记


     #排序


     plt.show()







