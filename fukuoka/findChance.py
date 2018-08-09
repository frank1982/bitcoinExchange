#coding=utf-8
#!/usr/bin/python

import myConfig
import threading
import mysql.connector
import time
import urllib2
import json
import myLogger
import dao
import datetime
import ctypes
import inspect


setting={

    "STEEMETH":{'huobiSell_bianBuy':0.1,'bianSell_huobiBuy':0.1},
    "EOSUSDT":{'huobiSell_bianBuy':0.1,'bianSell_huobiBuy':0.1},
}

def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")

def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)


def queryPrice(targetCoin,baseCoin):

    acktime=datetime.datetime.now()
    SYMBOL=targetCoin+baseCoin
    #myLogger.log("symbol:"+SYMBOL)
    limit_bianSell_huobiBuy=0.1
    limit_huobiSell_bianBuy=0.1
    for key in setting:

        if key == SYMBOL:

            limit_bianSell_huobiBuy=setting[SYMBOL]['bianSell_huobiBuy']
            limit_huobiSell_bianBuy=setting[SYMBOL]['huobiSell_bianBuy']
            break
    myLogger.log("symbol:%s:limit_bianSell_huobiBuy:limit_huobiSell_bianBuy:%f:%f"%(SYMBOL,limit_bianSell_huobiBuy,limit_huobiSell_bianBuy))



    while (1):


        #查询火币价格
        try:
            request = urllib2.Request('https://api.huobi.pro/market/depth?symbol='+targetCoin.lower()+baseCoin.lower()+'&type=step0')
            request.add_header('Content-Type', 'application/x-www-form-urlencoded')
            request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36')
            response = urllib2.urlopen(request,timeout = 15)
            data = json.load(response)
            huobi_lowestSellPrice=data["tick"]['asks'][0][0]
            huobi_lowestSellNum=data["tick"]['asks'][0][1]
            huobi_highestBuyPrice=data["tick"]['bids'][0][0]
            huobi_highestBuyNum=data["tick"]['bids'][0][1]

            #print '火币网最低卖价 %f' % huobi_lowestSellPrice
            #print '%s/%s火币网最高买价 %f' % (targetCoin,baseCoin,huobi_highestBuyPrice)

        except Exception,e:

            print e
            myLogger.log("%s:%s query price wrong in huobi" % (targetCoin,baseCoin))
            huobi_lowestSellPrice = -1000
            huobi_highestBuyPrice = -1000

        #查询币安价格
        try:
            targetCoin_Bian=targetCoin
            if targetCoin == "BCH":targetCoin_Bian="BCC"
            request2 = urllib2.Request('https://api.binance.com/api/v1/depth?symbol='+targetCoin_Bian+baseCoin)
            request2.add_header('Content-Type', 'application/x-www-form-urlencoded')
            response2 = urllib2.urlopen(request2,timeout = 15)
            data2 = json.load(response2)
            #print data2['asks'][0][0]
            bian_lowestSellPrice=float(data2['asks'][0][0])
            bian_highestBuyPrice=float(data2['bids'][0][0])
            bian_lowestSellNum=float(data2['asks'][0][1])
            bian_highestBuyNum=float(data2['bids'][0][1])
            #print bian_lowestSellPrice
            #print '币安网最低卖价 %f' % bian_lowestSellPrice
            #print '%s/%s币安网最高买价 %f' % (targetCoin_Bian,baseCoin,bian_highestBuyPrice)

        except Exception,e:
            #print e
            #print ("%s:%s query price wrong in bian" % (targetCoin_Bian,baseCoin))
            myLogger.log("%s:%s query price wrong in bian" % (targetCoin,baseCoin))
            bian_lowestSellPrice = -1000
            bian_highestBuyPrice = -1000


        #计算价格差
	    rate_bianSell_huobiBuy = -100
	    rate_huobiSell_bianBuy = -100
        if huobi_lowestSellPrice>0 and huobi_highestBuyPrice>0 and bian_lowestSellPrice>0 and bian_highestBuyPrice>0:

            baseprice=huobi_highestBuyPrice
            rate_bianSell_huobiBuy=(bian_highestBuyPrice-huobi_lowestSellPrice-bian_highestBuyPrice*0.001-huobi_lowestSellPrice*0.002)/baseprice*100
            rate_huobiSell_bianBuy=(huobi_highestBuyPrice-bian_lowestSellPrice-huobi_highestBuyPrice*0.002-bian_lowestSellPrice*0.001)/baseprice*100
            print("***Chance*QueryPrice***[%s/%s][%f/%f]" % (targetCoin,baseCoin,rate_bianSell_huobiBuy,rate_huobiSell_bianBuy))
                
            if rate_bianSell_huobiBuy >= limit_bianSell_huobiBuy or rate_huobiSell_bianBuy >= limit_huobiSell_bianBuy:

                print("***Chance*QueryPrice***[%s/%s][%f/%f]" % (targetCoin,baseCoin,rate_bianSell_huobiBuy,rate_huobiSell_bianBuy))
                #myLogger.log("***Chance*QueryPrice***[%s/%s][%f/%f]" % (targetCoin,baseCoin,rate_bianSell_huobiBuy,rate_huobiSell_bianBuy))
                timeStr=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                dao.insertQueryPriceData(
                    targetCoin,baseCoin,timeStr,rate_bianSell_huobiBuy,rate_huobiSell_bianBuy,
                    huobi_lowestSellPrice,huobi_highestBuyPrice,
                    huobi_lowestSellNum,huobi_highestBuyNum,
                    bian_lowestSellPrice,bian_highestBuyPrice,
                    bian_lowestSellNum,bian_highestBuyNum)



        else:
            #print 'one of price is null'
            pass
        #print '%s/%s : %f/%f' % (targetCoin_Bian,baseCoin,rate_bianSell_huobiBuy,rate_huobiSell_bianBuy)
        #ack心跳
        ackNow_time=datetime.datetime.now()
        if (ackNow_time-acktime).total_seconds() >= 1200: #5分钟心跳一次

            myLogger.log("[ACK*QueryPrice][%s/%s][%f/%f]" % (targetCoin,baseCoin,rate_bianSell_huobiBuy,rate_huobiSell_bianBuy))
            print("[ACK*QueryPrice][%s/%s][%f/%f]" % (targetCoin,baseCoin,rate_bianSell_huobiBuy,rate_huobiSell_bianBuy))
            acktime = datetime.datetime.now()
        
	time.sleep(0.5)


if __name__ == '__main__':

    symbolsList=[]#at least >=1
    threadsList=[]
    #改成从数据库里读取

    while (1):

        symbolsList=dao.getSymbols()
        myLogger.log(symbolsList)
        if len(symbolsList) > 0:

            for symbol in symbolsList:

                print  symbol
                targetCoin=symbol.split('/')[0]
                baseCoin=symbol.split('/')[1]
                thread = threading.Thread(target=queryPrice,args=(targetCoin,baseCoin,))
                thread.setDaemon(True)
                thread.start()
                threadsList.append(thread)

        else:
            print 'symbols list is null'

        time.sleep(7200)
        for index in range(len(threadsList)):
            try:
                th=threadsList[index]
                stop_thread(th)
                myLogger.log("%d thread exit" % index)
                print "thread exit"
            except Exception,e:
                myLogger.log(e)
                print e
        threadsList=[]


