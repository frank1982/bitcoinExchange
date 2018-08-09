
#coding=utf-8
#!/usr/bin/python
import time
import StringIO, gzip
import json, time, threading
import myLogger
import myConfig
import myAccount
import math
import ssl
import dao
import datetime
import notice
import sys
from ws4py.client.threadedclient import WebSocketClient
reload(sys)
sys.setdefaultencoding('utf8')


#定义全局变量
_flag_isHuobiSocketWork=True
_flag_isBianSocketWork=True

_highestBuyPrice_huobi=0
_highestBuyNum_huobi=0
_lowestSellPrice_huobi=0
_lowestSellNum_huobi=0
_highestBuyPrice_bian=0
_highestBuyNum_bian=0
_lowestSellPrice_bian=0
_lowestSellNum_bian=0

_balance_bian={}
_balance_huobi={}
_targetCoin=''
_baseCoin=''

def updateBalance():

    _balance_bian=myAccount.queryBalance_bian(_targetCoin,_baseCoin)
    _balance_huobi=myAccount.queryBalance_huobi(_targetCoin,_baseCoin)
    myLogger.log("update balance information:")
    myLogger.log("huobi: %s %s  %s %s" % (_targetCoin,_balance_huobi[_targetCoin],_baseCoin,_balance_huobi[_baseCoin]))
    myLogger.log("bian: %s %s  %s %s" % (_targetCoin,_balance_bian[_targetCoin],_baseCoin,_balance_bian[_baseCoin]))

    title="update balance information:"
    content1="huobi: %s %s  %s %s" % (_targetCoin,_balance_huobi[_targetCoin],_baseCoin,_balance_huobi[_baseCoin])
    content2="bian: %s %s  %s %s" % (_targetCoin,_balance_bian[_targetCoin],_baseCoin,_balance_bian[_baseCoin])
    sendNotice(title,content1,content2)

def enquireHuobiPrice():

    while (1):
       try:
            print 'websocket_endpoint_huobi start to connect'
            myLogger.log('websocket_endpoint_huobi start to connect')
            ws_huobi = DummyClient_huobi(myConfig.huobiRef['websocket_endpoint'],protocols=['http-only', 'chat'])
            ws_huobi.connect()
            ws_huobi.run_forever()
            break

       except Exception,e:

            myLogger.log("huobi websocket error")
            myLogger.log(e)
            try:
                ws_huobi.close()
            except Exception,e:

                myLogger.log("ws_huobi.close() error")
                myLogger.log(e)
            time.sleep(10)
            myLogger.log("will retry connect huobi websocket")


def gzdecode(data) :
    compressedstream = StringIO.StringIO(data)
    gziper = gzip.GzipFile(fileobj=compressedstream)
    data2 = gziper.read()   # 读取解压缩后数据
    return data2


class DummyClient_huobi(WebSocketClient):


    def opened(self):

        myLogger.log('huobi websocket opened')
        global _flag_isHuobiSocketWork
        _flag_isHuobiSocketWork=True
        tradeStr="""{"sub": "market.%s%s.depth.step0", "id": "id10"}""" % (_targetCoin.lower(),_baseCoin.lower())
        self.send(tradeStr)

    def closed(self, code, reason=None):

        myLogger.log("huobi websocket Closed down %s %s" %(code,reason))
        global _flag_isHuobiSocketWork
        _flag_isHuobiSocketWork=False
        time.sleep(180)
        enquireHuobiPrice()


    def received_message(self, m):

        try:
            msg=gzdecode(m).decode('utf-8')

            if msg[:7] == '{"ping"':
                ts=msg[8:21]
                pong='{"pong":'+ts+'}'
                self.send(pong)
                tradeStr="""{"sub": "market.%s%s.depth.step0", "id": "id10"}""" % (_targetCoin.lower(),_baseCoin.lower())
                self.send(tradeStr)

            else:

                if msg[:5] == '{"ch"':

                    priceData=json.loads(msg)
                    global _highestBuyPrice_huobi
                    global _highestBuyNum_huobi
                    global _lowestSellPrice_huobi
                    global _lowestSellNum_huobi


                    #bids 买
                    _highestBuyPrice_huobi=float(priceData['tick']['bids'][0][0])
                    _highestBuyNum_huobi=float(priceData['tick']['bids'][0][1])
                    #asks 卖
                    #print priceData
                    _lowestSellPrice_huobi=float(priceData['tick']['asks'][0][0])
                    _lowestSellNum_huobi=float(priceData['tick']['asks'][0][1])
                    #if not flag_isHuobiSocketWork:flag_isHuobiSocketWork=True
                    #价格显示出来核对下
                    #print "火币的最低卖价: "+"%f" % _lowestSellPrice_huobi
                    #print "火币的最低卖价深度: "+"%f" % lowestSellNum_huobi

        except Exception,e:

            myLogger.log("huobi on message error")
            myLogger.log(e)
            global _flag_isHuobiSocketWork
            _flag_isHuobiSocketWork=False


#24小时重启一次
def enquireBianPrice():

    #while (1):
        try:
            print 'try connect bian websocket'
            print _targetCoin.lower()
            print _baseCoin.lower()
            URL_BIAN=myConfig.binanceRef['websocket_endpoint']+'ws/%s%s@depth5' % (_targetCoin.lower(),_baseCoin.lower())
            print URL_BIAN
            ws_bian = DummyClient_bian(URL_BIAN,protocols=['http-only', 'chat'])
            #ws = DummyClient('ws://10.222.138.163:1889/websocket', protocols=['chat'])
            ws_bian.connect()
            ws_bian.run_forever()
            #break

        except Exception,e:

            myLogger.log("bian websocket error")
            myLogger.log(e)
            print "bian websocket error"
            print e
            try:
                ws_bian.close()
            except Exception,e:

                myLogger.log("ws_bian.close() error")
                myLogger.log(e)
                print e

            #time.sleep(10)
            #myLogger.log("will retry connect bian websocket")
            #print "will retry connect bian websocket"



class DummyClient_bian(WebSocketClient):#bian


    def opened(self):

        myLogger.log('bian websocket opened')
        print 'bian websocket opened'
        global _flag_isBianSocketWork
        _flag_isBianSocketWork=True

    def closed(self, code, reason=None):

        myLogger.log("bian websocket Closed down %s %s" %(code,reason))
        print "bian websocket Closed down %s %s" %(code,reason)
        global _flag_isBianSocketWork
        _flag_isBianSocketWork=False
        time.sleep(180)
        enquireBianPrice()

    def received_message(self, m):

        try:

            #if m.is_text:收到的是textMessage 格式
            recvStr = m.data.decode("utf-8")
            priceData = json.loads(recvStr)
            #print 'rec'
            #print   priceData

            global _highestBuyPrice_bian
            global _highestBuyNum_bian
            global _lowestSellPrice_bian
            global _lowestSellNum_bian

            _highestBuyPrice_bian=float(priceData["bids"][0][0])#最高买价
            _highestBuyNum_bian=float(priceData["bids"][0][1])
            _lowestSellPrice_bian=float(priceData["asks"][0][0])#最低卖价
            _lowestSellNum_bian=float(priceData["asks"][0][1])
            #print "_lowestSellPrice_bian %f" % _lowestSellPrice_bian


        except Exception,e:


            myLogger.log("bian on message error")
            print "bian on message error"
            print e
            myLogger.log(e)
            global _flag_isBianSocketWork
            _flag_isBianSocketWork=False



def sendNotice(title,content1,content2):

    remark="fukuoka"
    notice.sendTextInfo(title,content1,content2,remark)


def queryOrderDetail_bian(symbol,orderIdStr):


    while (1):

        tradeDetailResult=myAccount.getTradeDetail_bian(symbol,orderIdStr)
        myLogger.log("bian order result detail:")
        myLogger.log(tradeDetailResult)
        if not tradeDetailResult:

            myLogger.log("query result of bian order is null")
            exit()

        if tradeDetailResult['status'] == "FILLED":

            myLogger.log("bian trade is success in query detail cricle")

            title="bianBuy order success:"
            content1="buy number:%s" % tradeDetailResult['executedQty']
            content2="buy price:%s" % tradeDetailResult['price']
            sendNotice(title,content1,content2)

            #更新balance
            global _balance_bian
            global _balance_huobi
            _balance_bian=myAccount.queryBalance_bian(_targetCoin,_baseCoin)
            _balance_huobi=myAccount.queryBalance_huobi(_targetCoin,_baseCoin)
            myLogger.log("update balance information:")
            myLogger.log("huobi: %s %s  %s %s" % (_targetCoin,_balance_huobi[_targetCoin],_baseCoin,_balance_huobi[_baseCoin]))
            myLogger.log("bian: %s %s  %s %s" % (_targetCoin,_balance_bian[_targetCoin],_baseCoin,_balance_bian[_baseCoin]))

            title="update balance information:"
            content1="huobi: %s %s  %s %s" % (_targetCoin,_balance_huobi[_targetCoin],_baseCoin,_balance_huobi[_baseCoin])
            content2="bian: %s %s  %s %s" % (_targetCoin,_balance_bian[_targetCoin],_baseCoin,_balance_bian[_baseCoin])
            sendNotice(title,content1,content2)
            break

        time.sleep(300)

def saveActualPriceData(direction,rate,sellMarketNumber,buyMarketNumber):

    myLogger.log("saveActualPriceData")
    timeStr=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    dao.insertActualPriceData(timeStr,_symbol,direction,rate,sellMarketNumber,buyMarketNumber)


def queryOrderDetail_huobi(orderIdStr):

    while (1):

        tradeDetail=myAccount.getTradeDetail_huobi(orderIdStr)
        if tradeDetail:

             if tradeDetail['data']['state'] != "filled":#没有完成交易
                 myLogger.log("order of huobi is not finished")
                 myLogger.log(tradeDetail)

             else:#交易全部完成 state = filled

                 myLogger.log("buy order of huobi is finished")
                 title="huobiBuy order success:"
                 content1="BuyNum:%s" % tradeDetail['data']['field-amount']
                 content2="BuyPrice:%s" % tradeDetail['data']['price']
                 remark="fukuoka"
                 notice.sendTextInfo(title,content1,content2,remark)

                 #更新balance
                 global _balance_bian
                 global _balance_huobi
                 _balance_bian=myAccount.queryBalance_bian(_targetCoin,_baseCoin)
                 _balance_huobi=myAccount.queryBalance_huobi(_targetCoin,_baseCoin)
                 myLogger.log("update balance information:")
                 myLogger.log("huobi: %s %s  %s %s" % (_targetCoin,_balance_huobi[_targetCoin],_baseCoin,_balance_huobi[_baseCoin]))
                 myLogger.log("bian: %s %s  %s %s" % (_targetCoin,_balance_bian[_targetCoin],_baseCoin,_balance_bian[_baseCoin]))

                 title="update balance information:"
                 content1="huobi: %s %s  %s %s" % (_targetCoin,_balance_huobi[_targetCoin],_baseCoin,_balance_huobi[_baseCoin])
                 content2="bian: %s %s  %s %s" % (_targetCoin,_balance_bian[_targetCoin],_baseCoin,_balance_bian[_baseCoin])
                 sendNotice(title,content1,content2)

                 break#不再继续查询交易结果


        else:

            myLogger.log("query order detail error in huobi")
            break

        time.sleep(300)

#公共配置
_minNumOfLimitTrade={

    'EOS/USDT':1,#只能放一个值！
}



if __name__ == '__main__':


    _symbol=''
    _minTradeNumOfTargetCoin=0



    _acktime=datetime.datetime.now()
    _dayOnStart = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    _oldRate_huobiSell_bianBuy=0
    _oldRate_bianSell_huobiBuy=0
    _sellNumList_notBuyed_huobi=[]#火币 FAK/IOC交易如果产生小额交易，没有能够及时买入的累计在这里

    for key in _minNumOfLimitTrade:

        _targetCoin=key.split('/')[0]
        _baseCoin=key.split('/')[1]
        _minTradeNumOfTargetCoin=_minNumOfLimitTrade[key]

    _symbol=_targetCoin+_baseCoin

    _balance_bian=myAccount.queryBalance_bian(_targetCoin,_baseCoin)
    _balance_huobi=myAccount.queryBalance_huobi(_targetCoin,_baseCoin)


    #_tradeLimit_huobiSell_bianBuy=myConfig.tradeLimit[_symbol]['huobiSell_bianBuy']
    #_tradeLimit_bianSell_huobiBuy=myConfig.tradeLimit[_symbol]['bianSell_huobiBuy']
    tmpLimt=dao.getTradeLimit(_symbol)
    _tradeLimit_huobiSell_bianBuy=tmpLimt['huobiSell_bianBuy']
    _tradeLimit_bianSell_huobiBuy=tmpLimt['bianSell_huobiBuy']
    print "tradeLimit:huobiSell_bianBuy:%f:bianSell_huobiBuy:%f"%(_tradeLimit_huobiSell_bianBuy,_tradeLimit_bianSell_huobiBuy)

    myLogger.log("tradeLimit:huobiSell_bianBuy:%f:bianSell_huobiBuy:%f"%(_tradeLimit_huobiSell_bianBuy,_tradeLimit_bianSell_huobiBuy))

    if not _balance_bian or not _balance_huobi:#只要有一个账户没有查到余额就推出程序

        myLogger.log("one balance is empty")
        print "one balance is empty"
        exit()

    myLogger.log("now balance information:")
    myLogger.log("huobi: %s %s  %s %s" % (_targetCoin,_balance_huobi[_targetCoin],_baseCoin,_balance_huobi[_baseCoin]))
    myLogger.log("bian: %s %s  %s %s" % (_targetCoin,_balance_bian[_targetCoin],_baseCoin,_balance_bian[_baseCoin]))

    title="now balance information:"
    content1="huobi: %s %s  %s %s" % (_targetCoin,_balance_huobi[_targetCoin],_baseCoin,_balance_huobi[_baseCoin])
    content2="bian: %s %s  %s %s" % (_targetCoin,_balance_bian[_targetCoin],_baseCoin,_balance_bian[_baseCoin])
    sendNotice(title,content1,content2)


    #开启价格查询
    print 'will get price data'
    threads = []
    t_huobi = threading.Thread(target=enquireHuobiPrice)
    threads.append(t_huobi)
    t_bian = threading.Thread(target=enquireBianPrice)
    threads.append(t_bian)
    for t in threads:

        t.setDaemon(True)
        t.start()

    print 'will start main circle'
    #主循环
    while (1):


         #先判断websocket是否正常
         if not _flag_isHuobiSocketWork or not _flag_isBianSocketWork:#有一个websocket没有工作

            myLogger.log("at least one websocket does not work")
            time.sleep(5)
            continue

         if _highestBuyPrice_huobi<=0 or _highestBuyPrice_bian <=0:#没有取到价格

            myLogger.log("does not get price data")
            time.sleep(5)
            continue

         #把火币已经卖出，币安还没有买入的找机会买入
         #原因是来自火币买入的 IOC 订单
         #_sellNumList_notBuyed_huobi=[]#火币 FAK/IOC交易如果产生小额交易，没有能够及时买入的累计在这里




         #判断价格是否达到触发条件
         #这里不能直接使用价格信息，避免数据在同时被修改
         tmp_lowestSellPrice_bian=_lowestSellPrice_bian
         tmp_highestBuyPrice_bian=_highestBuyPrice_bian
         tmp_lowestSellPrice_huobi=_lowestSellPrice_huobi
         tmp_highestBuyPrice_huobi=_highestBuyPrice_huobi

         tmp_lowestSellNum_bian=_lowestSellNum_bian
         tmp_highestBuyNum_bian=_highestBuyNum_bian
         tmp_lowestSellNum_huobi=_lowestSellNum_huobi
         tmp_highestBuyNum_huobi=_highestBuyNum_huobi

         #print tmp_lowestSellNum_bian


         baseprice=tmp_highestBuyPrice_huobi #基准价格
         grossRevenue_huobiSell_bianBuy = tmp_highestBuyPrice_huobi-tmp_lowestSellPrice_bian
         grossRevenue_bianSell_huobiBuy = tmp_highestBuyPrice_bian-tmp_lowestSellPrice_huobi


         #cost都是从交易结果中扣除，以1个单位target coin为例
         cost_bianSell_huobiBuy = myConfig.binanceRef['tradeCost']*tmp_highestBuyPrice_bian+myConfig.huobiRef['tradeCost']*tmp_lowestSellPrice_huobi
         cost_huobiSell_bianBuy = myConfig.huobiRef['tradeCost']*tmp_highestBuyPrice_huobi+myConfig.binanceRef['tradeCost']*tmp_lowestSellPrice_bian

         #减去交易成本
         profit_bianSell_huobiBuy = grossRevenue_bianSell_huobiBuy-cost_bianSell_huobiBuy
         profit_huobiSell_bianBuy = grossRevenue_huobiSell_bianBuy-cost_huobiSell_bianBuy
         profitRate_bianSell_huobiBuy = profit_bianSell_huobiBuy/baseprice*100
         profitRate_huobiSell_bianBuy = profit_huobiSell_bianBuy/baseprice*100

         #每天做一次统计
         dayNow = time.strftime('%Y-%m-%d',time.localtime(time.time()))
         if dayNow > _dayOnStart:#新的一天

            _dayOnStart = dayNow
            #统计一天内的数据并发送
            myLogger.log("a new day")
            '''
            myLogger.log("ACKTRADE*bianSell_huobiBuy:%f*huobiSell_bianBuy:%f" % (profitRate_bianSell_huobiBuy,profitRate_huobiSell_bianBuy))
            #更新balance
            _balance_bian=myAccount.queryBalance_bian(_targetCoin,_baseCoin)
            _balance_huobi=myAccount.queryBalance_huobi(_targetCoin,_baseCoin)
            title="i am working,now balance:"
            content1="huobi: %s %s  %s %s" % (_targetCoin,_balance_huobi[_targetCoin],_baseCoin,_balance_huobi[_baseCoin])
            content2="bian: %s %s  %s %s" % (_targetCoin,_balance_bian[_targetCoin],_baseCoin,_balance_bian[_baseCoin])
            sendNotice(title,content1,content2)
            '''


 

         #ack心跳
         ackNow_time=datetime.datetime.now()
         if (ackNow_time-_acktime).total_seconds() >= 7200: #20分钟心跳一次

             myLogger.log("ACKTRADE*bianSell_huobiBuy:%f*huobiSell_bianBuy:%f" % (profitRate_bianSell_huobiBuy,profitRate_huobiSell_bianBuy))
             #更新balance
             _balance_bian=myAccount.queryBalance_bian(_targetCoin,_baseCoin)
             _balance_huobi=myAccount.queryBalance_huobi(_targetCoin,_baseCoin)
             title="i am working,now balance:"
             content1="huobi: %s %s  %s %s" % (_targetCoin,_balance_huobi[_targetCoin],_baseCoin,_balance_huobi[_baseCoin])
             content2="bian: %s %s  %s %s" % (_targetCoin,_balance_bian[_targetCoin],_baseCoin,_balance_bian[_baseCoin])
             sendNotice(title,content1,content2)
             #_sellNumList_notBuyed_huobi
             #更改设定的交易限额
             tmpLimt=dao.getTradeLimit(_symbol)
             _tradeLimit_huobiSell_bianBuy=tmpLimt['huobiSell_bianBuy']
             _tradeLimit_bianSell_huobiBuy=tmpLimt['bianSell_huobiBuy']
             title="now trade limit:"
             content1="huobiSell_bianBuy: %f" % _tradeLimit_huobiSell_bianBuy
             content2="bianSell_huobiBuy: %f" % _tradeLimit_bianSell_huobiBuy
             sendNotice(title,content1,content2)
             _acktime = datetime.datetime.now()

         if _oldRate_huobiSell_bianBuy<>profitRate_huobiSell_bianBuy or _oldRate_bianSell_huobiBuy<>profitRate_bianSell_huobiBuy:

            print ("bianSell_huobiBuy:%f*huobiSell_bianBuy:%f" % (profitRate_bianSell_huobiBuy,profitRate_huobiSell_bianBuy))

         #判断交易机会
         #没有达到任何一边的的交易要求
         if profitRate_bianSell_huobiBuy < _tradeLimit_bianSell_huobiBuy and profitRate_huobiSell_bianBuy < _tradeLimit_huobiSell_bianBuy:

             _oldRate_huobiSell_bianBuy=profitRate_huobiSell_bianBuy
             _oldRate_bianSell_huobiBuy=profitRate_bianSell_huobiBuy
             continue

         #至少达到了一边的交易要求，打印一下信息,异步保存下价格信息
         #防止重复打印log
         if _oldRate_huobiSell_bianBuy<>profitRate_huobiSell_bianBuy or _oldRate_bianSell_huobiBuy<>profitRate_bianSell_huobiBuy:

            myLogger.log("reachTradeCondition*bianSell_huobiBuy:%f*huobiSell_bianBuy:%f" % (profitRate_bianSell_huobiBuy,profitRate_huobiSell_bianBuy))
            print ("reachTradeCondition*bianSell_huobiBuy:%f*huobiSell_bianBuy:%f" % (profitRate_bianSell_huobiBuy,profitRate_huobiSell_bianBuy))

         #达到币安卖出火币买入条件
         if profitRate_bianSell_huobiBuy >= _tradeLimit_bianSell_huobiBuy:


             #防止重复
             if _oldRate_huobiSell_bianBuy<>profitRate_huobiSell_bianBuy or _oldRate_bianSell_huobiBuy<>profitRate_bianSell_huobiBuy:

                 #异步保存价格信息
                 t_savePriceData = threading.Thread(
                    target=saveActualPriceData,
                    args=("bianSell_huobiBuy",profitRate_bianSell_huobiBuy,tmp_highestBuyNum_bian,tmp_lowestSellNum_huobi,))
                 t_savePriceData.setDaemon(True)
                 t_savePriceData.start()


             #判断进入的机会，不能偏离成本价格太多
             if tmp_highestBuyPrice_bian < myConfig.orderLimit[_symbol]['costPrice']*(1-myConfig.orderLimit[_symbol]['offset']):

                 #卖出价格太低，不进行交易
                 #防止重复打印log
                 if _oldRate_huobiSell_bianBuy<>profitRate_huobiSell_bianBuy or _oldRate_bianSell_huobiBuy<>profitRate_bianSell_huobiBuy:

                     myLogger.log("%f is too lower, stop order" % tmp_highestBuyPrice_bian)

                 _oldRate_huobiSell_bianBuy=profitRate_huobiSell_bianBuy
                 _oldRate_bianSell_huobiBuy=profitRate_bianSell_huobiBuy
                 continue

             #判断本次交易的余额够不够
             if _balance_bian[_targetCoin] < _minTradeNumOfTargetCoin:#不足

                 #防止重复打印log
                 if _oldRate_huobiSell_bianBuy<>profitRate_huobiSell_bianBuy or _oldRate_bianSell_huobiBuy<>profitRate_bianSell_huobiBuy:

                     myLogger.log("bian balance targetCoin is not enough: %f" % _balance_bian[_targetCoin])

                 _oldRate_huobiSell_bianBuy=profitRate_huobiSell_bianBuy
                 _oldRate_bianSell_huobiBuy=profitRate_bianSell_huobiBuy
                 continue

             #判断买入账户余额够不够
             #不足
             if _balance_huobi[_baseCoin] < _balance_bian[_targetCoin]*tmp_lowestSellPrice_huobi*1.003:

                 #防止重复打印log
                 if _oldRate_huobiSell_bianBuy<>profitRate_huobiSell_bianBuy or _oldRate_bianSell_huobiBuy<>profitRate_bianSell_huobiBuy:

                     myLogger.log("huobi balance baseCoin is not enough: %f" % _balance_huobi[_baseCoin])

                 _oldRate_huobiSell_bianBuy=profitRate_huobiSell_bianBuy
                 _oldRate_bianSell_huobiBuy=profitRate_bianSell_huobiBuy
                 continue

             #账户余额检查完成

             #检查本次交易的金额是否达到最小的交易金额限制，因为币安是AOK，要么成功全部成功，要么全部失败
             #达不到最小交易限额的不能交易
             if min(tmp_highestBuyNum_bian,tmp_lowestSellNum_huobi) < _minTradeNumOfTargetCoin:

                #防止重复打印log
                 if _oldRate_huobiSell_bianBuy<>profitRate_huobiSell_bianBuy or _oldRate_bianSell_huobiBuy<>profitRate_bianSell_huobiBuy:

                     myLogger.log("trade num is too small tmp_highestBuyNum_bian:%f tmp_lowestSellNum_huobi:%f" %(tmp_highestBuyNum_bian,tmp_lowestSellNum_huobi))

                 _oldRate_huobiSell_bianBuy=profitRate_huobiSell_bianBuy
                 _oldRate_bianSell_huobiBuy=profitRate_bianSell_huobiBuy
                 continue

             targetCoinSellNum=min(tmp_highestBuyNum_bian,tmp_lowestSellNum_huobi,_balance_bian[_targetCoin])
             targetCoinSellNum=targetCoinSellNum-0.01
             targetCoinSellNum=round(targetCoinSellNum,2)

             #EOSUSDT price 精度小数点后四位
             targetCoinSellPrice=tmp_highestBuyPrice_bian-0.0002
             targetCoinSellPrice=round(targetCoinSellPrice,4)
             targetCoinBuyNum = targetCoinSellNum/0.998
             targetCoinBuyNum = round(targetCoinBuyNum,2)
             targetCoinBuyPrice=tmp_lowestSellPrice_huobi+0.0002
             targetCoinBuyPrice=round(targetCoinBuyPrice,4)

             #STEEMETH
             '''
             targetCoinSellPrice=tmp_highestBuyPrice_bian-0.000002
             targetCoinSellPrice=round(targetCoinSellPrice,6)
             targetCoinBuyNum = targetCoinSellNum/0.998
             targetCoinBuyNum = round(targetCoinBuyNum,4)
             targetCoinBuyPrice=tmp_lowestSellPrice_huobi+0.000002
             targetCoinBuyPrice=round(targetCoinBuyPrice,6)
             '''
             myLogger.log("bian sellNum:%f sellPrice:%f"%(targetCoinSellNum,targetCoinSellPrice))
             myLogger.log("huobi buyNum:%f buyPrice:%f"%(targetCoinBuyNum,targetCoinBuyPrice))

             #bian是FOK订单，不存在挂单可能
             orderResult_bian=myAccount.order_bian("SELL",_targetCoin,_baseCoin,targetCoinSellNum,targetCoinSellPrice)
             if orderResult_bian != "SUCCESS":#币安没有卖出成功

                myLogger.log("bian sell error")
                _oldRate_huobiSell_bianBuy=profitRate_huobiSell_bianBuy
                _oldRate_bianSell_huobiBuy=profitRate_bianSell_huobiBuy
                title="bian sell error:"
                content1="bian fok sell error!"
                content2="what is wrong"
                sendNotice(title,content1,content2)
                continue

             #币安卖出成功
             myLogger.log('bianSell success')
             #火币买入,limit订单
             orderResult_huobi=myAccount.order_huobi("BUY",_targetCoin.lower(),_baseCoin.lower(),targetCoinBuyNum,targetCoinBuyPrice)
             if orderResult_huobi['status'] != "ok":#火币买入不一定，有可能超时！

                _oldRate_huobiSell_bianBuy=profitRate_huobiSell_bianBuy
                _oldRate_bianSell_huobiBuy=profitRate_bianSell_huobiBuy
                title="huobi buy maybe error or outtime:"
                content1="huobi buy  error or outtime!"
                content2=orderResult_huobi
                sendNotice(title,content1,content2)

                time.sleep(20)
                #更新余额
                _balance_bian=myAccount.queryBalance_bian(_targetCoin,_baseCoin)
                _balance_huobi=myAccount.queryBalance_huobi(_targetCoin,_baseCoin)

                title="update balance information:"
                content1="huobi: %s %s  %s %s" % (_targetCoin,_balance_huobi[_targetCoin],_baseCoin,_balance_huobi[_baseCoin])
                content2="bian: %s %s  %s %s" % (_targetCoin,_balance_bian[_targetCoin],_baseCoin,_balance_bian[_baseCoin])
                sendNotice(title,content1,content2)

                continue

             #火币买入完成,也有可能是挂单
             orderId=orderResult_huobi['data']
             myLogger.log('will query huobi orderId:'+orderId)
             #开启火币交易结果查询
             _oldRate_huobiSell_bianBuy=profitRate_huobiSell_bianBuy
             _oldRate_bianSell_huobiBuy=profitRate_bianSell_huobiBuy
             title="bianSell success:"
             content1="SellNum:%s" % targetCoinSellNum
             content2="SellPrice:%s" % targetCoinSellPrice
             sendNotice(title,content1,content2)

             time.sleep(5)
             t_queryHuobiOrder = threading.Thread(target=queryOrderDetail_huobi,args=(orderId,))
             t_queryHuobiOrder.setDaemon(True)
             t_queryHuobiOrder.start()


             #更新balance,防止余额还没有变化

             _balance_bian=myAccount.queryBalance_bian(_targetCoin,_baseCoin)
             _balance_huobi=myAccount.queryBalance_huobi(_targetCoin,_baseCoin)
             myLogger.log("update balance information:")
             myLogger.log("huobi: %s %s  %s %s" % (_targetCoin,_balance_huobi[_targetCoin],_baseCoin,_balance_huobi[_baseCoin]))
             myLogger.log("bian: %s %s  %s %s" % (_targetCoin,_balance_bian[_targetCoin],_baseCoin,_balance_bian[_baseCoin]))

             title="update balance information:"
             content1="huobi: %s %s  %s %s" % (_targetCoin,_balance_huobi[_targetCoin],_baseCoin,_balance_huobi[_baseCoin])
             content2="bian: %s %s  %s %s" % (_targetCoin,_balance_bian[_targetCoin],_baseCoin,_balance_bian[_baseCoin])
             sendNotice(title,content1,content2)



         #达到火币卖出币安买入条件
         elif profitRate_huobiSell_bianBuy >= _tradeLimit_huobiSell_bianBuy:

             #防止重复
             if _oldRate_huobiSell_bianBuy<>profitRate_huobiSell_bianBuy or _oldRate_bianSell_huobiBuy<>profitRate_bianSell_huobiBuy:

                 #异步保存价格信息
                 t_savePriceData = threading.Thread(
                    target=saveActualPriceData,
                    args=("huobiSell_bianBuy",profitRate_huobiSell_bianBuy,tmp_highestBuyNum_huobi,tmp_lowestSellNum_bian,))
                 t_savePriceData.setDaemon(True)
                 t_savePriceData.start()

             #判断进入机会，卖出价格不能偏离成本价格太多
             if tmp_highestBuyPrice_huobi < myConfig.orderLimit[_symbol]['costPrice']*(1-myConfig.orderLimit[_symbol]['offset']):

                 #卖出价格太低，不进行交易
                 #防止重复打印log
                 if (_oldRate_huobiSell_bianBuy<>profitRate_huobiSell_bianBuy or _oldRate_bianSell_huobiBuy<>profitRate_bianSell_huobiBuy):

                     myLogger.log("%f is too lower, stop order" % tmp_highestBuyPrice_huobi)

                 _oldRate_huobiSell_bianBuy=profitRate_huobiSell_bianBuy
                 _oldRate_bianSell_huobiBuy=profitRate_bianSell_huobiBuy
                 continue


             #火币账户不足
             if _balance_huobi[_targetCoin] < _minTradeNumOfTargetCoin:

                 #防止重复打印log
                 if _oldRate_huobiSell_bianBuy<>profitRate_huobiSell_bianBuy or _oldRate_bianSell_huobiBuy<>profitRate_bianSell_huobiBuy:

                     myLogger.log("huobi balance targetCoin is not enough: %f" % _balance_huobi[_targetCoin])

                 _oldRate_huobiSell_bianBuy=profitRate_huobiSell_bianBuy
                 _oldRate_bianSell_huobiBuy=profitRate_bianSell_huobiBuy
                 continue

             #另一侧账户baseCoin买入资金够不够?
             if _balance_bian[_baseCoin] < _balance_huobi[_targetCoin]*tmp_lowestSellPrice_bian*1.003:

                 #防止重复打印log
                 if (_oldRate_huobiSell_bianBuy<>profitRate_huobiSell_bianBuy or _oldRate_bianSell_huobiBuy<>profitRate_bianSell_huobiBuy):

                     myLogger.log("bian balance baseCoin is not enough: %f" % _balance_bian[_baseCoin])

                 _oldRate_huobiSell_bianBuy=profitRate_huobiSell_bianBuy
                 _oldRate_bianSell_huobiBuy=profitRate_bianSell_huobiBuy
                 continue

             #账户余额检查完成
             #达不到最小交易限额的不能交易,火币卖出币安买入条件
             if min(tmp_highestBuyNum_huobi,tmp_lowestSellNum_bian) < _minTradeNumOfTargetCoin:

                 #防止重复打印log
                 if _oldRate_huobiSell_bianBuy<>profitRate_huobiSell_bianBuy or _oldRate_bianSell_huobiBuy<>profitRate_bianSell_huobiBuy:

                     myLogger.log("trade num is too small tmp_highestBuyNum_huobi:%f tmp_lowestSellNum_bian:%f" %(tmp_highestBuyNum_huobi,tmp_lowestSellNum_bian))

                 _oldRate_huobiSell_bianBuy=profitRate_huobiSell_bianBuy
                 _oldRate_bianSell_huobiBuy=profitRate_bianSell_huobiBuy
                 continue

             #火币卖出币安买入 EOSUSDT精度不一样
             targetCoinSellNum=min(tmp_highestBuyNum_huobi,tmp_lowestSellNum_bian,_balance_huobi[_targetCoin])
             targetCoinSellNum=targetCoinSellNum-0.01
             targetCoinSellNum=round(targetCoinSellNum,2)
             finalTargetCoinSellNum=targetCoinSellNum#火币的 ioc 交易有可能造成实际成交数量不同
             targetCoinSellPrice=tmp_highestBuyPrice_huobi-0.0002
             targetCoinSellPrice=round(targetCoinSellPrice,4)

             '''
             #火币卖出币安买入
             targetCoinSellNum=min(tmp_highestBuyNum_huobi,tmp_lowestSellNum_bian,_balance_huobi[_targetCoin])
             targetCoinSellNum=targetCoinSellNum-0.01
             targetCoinSellNum=round(targetCoinSellNum,2)
             finalTargetCoinSellNum=targetCoinSellNum#火币的 ioc 交易有可能造成实际成交数量不同
             targetCoinSellPrice=tmp_highestBuyPrice_huobi-0.000002
             targetCoinSellPrice=round(targetCoinSellPrice,6)
             '''

             #暂时先不计算出要在币安买入的数量

             #targetCoinBuyNum = targetCoinSellNum/0.998
             #targetCoinBuyNum = round(targetCoinBuyNum,5)
             #targetCoinBuyPrice=tmp_lowestSellPrice_bian+0.000001
             #targetCoinBuyPrice=round(targetCoinBuyPrice,6)

             #


             myLogger.log("huobi sellNum:%f sellPrice:%f"%(targetCoinSellNum,targetCoinSellPrice))


             #火币卖出 FAK 交易 可以部分成交
             #_sellNumList_notBuyed_huobi
             orderResult_huobi=myAccount.order_huobi_IOC("SELL",_targetCoin.lower(),_baseCoin.lower(),targetCoinSellNum,targetCoinSellPrice)
             if orderResult_huobi['status'] != "ok":#火币没有卖出完成

                 myLogger.log("huobi sell error")
                 _oldRate_huobiSell_bianBuy=profitRate_huobiSell_bianBuy
                 _oldRate_bianSell_huobiBuy=profitRate_bianSell_huobiBuy
                 title="huobi sell error:"
                 content1="huobi sell error!"
                 content2="huobi is wrong"
                 sendNotice(title,content1,content2)
                 continue

             #火币卖出完成，注意不一定全部成交，需要查询成交金额
             '''
             {u'status': u'ok', u'data': {
                u'account-id': 848426, u'canceled-at': 0, u'finished-at': 0,
                u'field-cash-amount': u'0.0', u'price': u'0.003500000000000000',
                u'created-at': 1529036734953, u'state': u'submitted', u'id': 5897652170,
                u'field-amount': u'0.0', u'amount': u'2.000000000000000000',
                u'source': u'api', u'field-fees': u'0.0', u'type': u'sell-ioc',
                u'symbol': u'steemeth'}
             }
             '''
             orderId=orderResult_huobi['data']
             myLogger.log('will query huobi orderId:'+orderId)
             while (1):#开启结果查询

                 tradeDetail=myAccount.getTradeDetail_huobi(orderId)
                 if not tradeDetail:#查询结果为空,结束程序

                     myLogger.log("can not get huobi order detail, is null")
                     title="query huobi error:"
                     content1="query huobi error!"
                     content2="stop task"
                     sendNotice(title,content1,content2)
                     exit()

                 if tradeDetail['data']['state'] == 'canceled':#没有成交

                     finalTargetCoinSellNum=0
                     myLogger.log("order of huobi is canceled")
                     title="huobi order canceled"
                     content1="huobi order is canceled"
                     content2="continue"
                     sendNotice(title,content1,content2)
                     break

                 if tradeDetail['data']['state'] == "filled" or tradeDetail['data']['state'] == 'partial-canceled':#完成交易了

                     finalTargetCoinSellNum=float(tradeDetail['data']['field-amount'])
                     myLogger.log("order of huobi is finished")
                     myLogger.log(tradeDetail)
                     myLogger.log('finalTargetCoinSellNum:%f' % finalTargetCoinSellNum)
                     break#结束查询


                 myLogger.log("tradeDetail")
                 myLogger.log(tradeDetail)


             #继续 币安买入的交易，但是实际成交数量可能变化
             #分析火币卖出的数量
             myLogger.log('huobiSell finish')
             myLogger.log('huobiSell final num: %f'%finalTargetCoinSellNum)

             if finalTargetCoinSellNum < _minTradeNumOfTargetCoin:#实际成交数量小于限定值，暂存

                 _oldRate_huobiSell_bianBuy=profitRate_huobiSell_bianBuy
                 _oldRate_bianSell_huobiBuy=profitRate_bianSell_huobiBuy
                 title="huobi sell finish but too small:"
                 content1="sellNum: %f" % finalTargetCoinSellNum
                 content2="sellPrice: %f " % targetCoinSellPrice
                 sendNotice(title,content1,content2)


                 if finalTargetCoinSellNum > 0:

                    tmpTrade={'sellNum':finalTargetCoinSellNum,'sellPrice':targetCoinSellPrice}
                    _sellNumList_notBuyed_huobi.append(tmpTrade)
                    myLogger.log('_sellNumList_notBuyed_huobi.append:')
                    myLogger.log(_sellNumList_notBuyed_huobi)
                    #更新balance
                    _balance_bian=myAccount.queryBalance_bian(_targetCoin,_baseCoin)
                    _balance_huobi=myAccount.queryBalance_huobi(_targetCoin,_baseCoin)

                    myLogger.log("update balance information:")
                    myLogger.log("huobi: %s %s  %s %s" % (_targetCoin,_balance_huobi[_targetCoin],_baseCoin,_balance_huobi[_baseCoin]))
                    myLogger.log("bian: %s %s  %s %s" % (_targetCoin,_balance_bian[_targetCoin],_baseCoin,_balance_bian[_baseCoin]))

                    title="update balance information:"
                    content1="huobi: %s %s  %s %s" % (_targetCoin,_balance_huobi[_targetCoin],_baseCoin,_balance_huobi[_baseCoin])
                    content2="bian: %s %s  %s %s" % (_targetCoin,_balance_bian[_targetCoin],_baseCoin,_balance_bian[_baseCoin])
                    sendNotice(title,content1,content2)

                 continue

             #EOSUSDT精度
             #实际成交数量大于限定值，继续币安的买入交易
             targetCoinBuyNum = finalTargetCoinSellNum/0.998
             targetCoinBuyNum = round(targetCoinBuyNum,2)
             targetCoinBuyPrice=tmp_lowestSellPrice_bian+0.0002
             targetCoinBuyPrice=round(targetCoinBuyPrice,4)
             '''
             #实际成交数量大于限定值，继续币安的买入交易
             targetCoinBuyNum = finalTargetCoinSellNum/0.998
             targetCoinBuyNum = round(targetCoinBuyNum,2)
             targetCoinBuyPrice=tmp_lowestSellPrice_bian+0.000002
             targetCoinBuyPrice=round(targetCoinBuyPrice,6)
             '''
             orderResult_bian=myAccount.order_bian_GTC("BUY",_targetCoin,_baseCoin,targetCoinBuyNum,targetCoinBuyPrice)
             myLogger.log("bian buy order start:")
             myLogger.log("buyNum:%f buyPrice:%f"%(targetCoinBuyNum,targetCoinBuyPrice))
             myLogger.log("orderResult_bian:")
             myLogger.log(orderResult_bian)

             '''
             if not orderResult_bian:

                 myLogger.log('bian buy order error')
                 title="bian buy order error:"
                 content1="bian buy order error!"
                 content2="stop task"
                 sendNotice(title,content1,content2)
                 exit()
             '''

             title="huobiSell success:"
             content1="SellNum: %f" % finalTargetCoinSellNum
             content2="SellPrice: %f" % targetCoinSellPrice
             sendNotice(title,content1,content2)
             _oldRate_huobiSell_bianBuy=profitRate_huobiSell_bianBuy
             _oldRate_bianSell_huobiBuy=profitRate_bianSell_huobiBuy

             time.sleep(5)
             if orderResult_bian['status'] != 'FILLED':#挂单 NEW

                 #循环查询，另起线程
                 orderId=orderResult_bian['orderId']
                 t_queryBianOrder = threading.Thread(target=queryOrderDetail_bian,args=(_symbol,orderId,))
                 t_queryBianOrder.setDaemon(True)
                 t_queryBianOrder.start()


                 #更新balance
                 _balance_bian=myAccount.queryBalance_bian(_targetCoin,_baseCoin)
                 _balance_huobi=myAccount.queryBalance_huobi(_targetCoin,_baseCoin)

                 myLogger.log("update balance information:")
                 myLogger.log("huobi: %s %s  %s %s" % (_targetCoin,_balance_huobi[_targetCoin],_baseCoin,_balance_huobi[_baseCoin]))
                 myLogger.log("bian: %s %s  %s %s" % (_targetCoin,_balance_bian[_targetCoin],_baseCoin,_balance_bian[_baseCoin]))

                 title="update balance information:"
                 content1="huobi: %s %s  %s %s" % (_targetCoin,_balance_huobi[_targetCoin],_baseCoin,_balance_huobi[_baseCoin])
                 content2="bian: %s %s  %s %s" % (_targetCoin,_balance_bian[_targetCoin],_baseCoin,_balance_bian[_baseCoin])
                 sendNotice(title,content1,content2)


                 continue

             #币安买入成功
             #币安交易成功 FILLED

             myLogger.log("bian buy order success")
             myLogger.log("buyNum:%f buyPrice:%f"%(targetCoinBuyNum,targetCoinBuyPrice))


             title="bianBuy success:"
             content1="BuyNum: %f" % targetCoinBuyNum
             content2="BuyPrice: %f" % targetCoinBuyPrice
             sendNotice(title,content1,content2)


             #更新balance

             _balance_bian=myAccount.queryBalance_bian(_targetCoin,_baseCoin)
             _balance_huobi=myAccount.queryBalance_huobi(_targetCoin,_baseCoin)


             myLogger.log("update balance information:")
             myLogger.log("huobi: %s %s  %s %s" % (_targetCoin,_balance_huobi[_targetCoin],_baseCoin,_balance_huobi[_baseCoin]))
             myLogger.log("bian: %s %s  %s %s" % (_targetCoin,_balance_bian[_targetCoin],_baseCoin,_balance_bian[_baseCoin]))

             title="update balance information:"
             content1="huobi: %s %s  %s %s" % (_targetCoin,_balance_huobi[_targetCoin],_baseCoin,_balance_huobi[_baseCoin])
             content2="bian: %s %s  %s %s" % (_targetCoin,_balance_bian[_targetCoin],_baseCoin,_balance_bian[_baseCoin])
             sendNotice(title,content1,content2)


