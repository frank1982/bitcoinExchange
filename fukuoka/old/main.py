
#coding=utf-8
#!/usr/bin/python
import websocket
from websocket import create_connection
import time
import StringIO, gzip
import json, time, threading
import logger
import dao
import math
import config
import ssl
import account
import datetime
import notice
import sys
from ws4py.client.threadedclient import WebSocketClient
reload(sys)
sys.setdefaultencoding('utf8')


targetCoin=''
baseCoin=''




def checkTradeResult(targetCoin,baseCoin,balance_huobi,balance_bian,baseprice,quantity):

    #联网查询下账户余额
    logger.log("check trade group results")

    while (1):
        balance_bian_new=account.queryBalance_bian(targetCoin,baseCoin)
        balance_huobi_new=account.queryBalance_huobi(targetCoin,baseCoin)
        if balance_bian_new and balance_huobi_new:break
        logger.log("retry query balance in check trade result")

    balance_new={}
    balance_new['balance_bian_new']=balance_bian_new
    balance_new['balance_huobi_new']=balance_huobi_new

    #Coin变化
    delta_targetCoin=balance_bian_new[targetCoin]+balance_huobi_new[targetCoin]-balance_bian[targetCoin]-balance_huobi[targetCoin]
    delta_baseCoin=balance_bian_new[baseCoin]+balance_huobi_new[baseCoin]-balance_bian[baseCoin]-balance_huobi[baseCoin]

    #结算盈亏
    finalRescult = delta_targetCoin*baseprice+delta_baseCoin
    finalRescultRate = finalRescult/(quantity*baseprice)*100#盈亏占本次交易的比例
    logger.log("final revenue %s 结算: %f %f" % (baseCoin,finalRescult,finalRescultRate))
    #insertBalanceTable(targetCoin,baseCoin,balance_targetCoin_bian,balance_baseCoin_bian,balance_targetCoin_huobi,balance_baseCoin_huobi):
    dao.insertBalanceTable(targetCoin,baseCoin,
                           balance_bian_new[targetCoin],
                           balance_bian_new[baseCoin],
                           balance_huobi_new[targetCoin],
                           balance_huobi_new[baseCoin])


    #send notice
    titleStr = "kyoto核对结果"
    content1Str = "火币账户:%s余额%.8f%s余额%.8f" % (targetCoin,balance_huobi_new[targetCoin],baseCoin,balance_huobi_new[baseCoin])
    content2Str = "币安账户:%s余额%.8f%s余额%.8f" % (targetCoin,balance_bian_new[targetCoin],baseCoin,balance_bian_new[baseCoin])
    remarkStr =  "本次交易对最终盈亏按%s最终结算收益:%f收益率:%f" % (baseCoin,finalRescult,finalRescultRate)
    notice.sendTextInfo(titleStr,content1Str,content2Str,remarkStr)

    return balance_new


def huobiBuy(buybase):#子线程执行的方法

    global flag_isHuobiBuyThreadInTrade
    orderResult_huobi = ""
    orderResult_huobi=account.order_huobi_market("BUY",targetCoin.lower(),baseCoin.lower(),buybase)
    #分析火币网买入的结果
    if orderResult_huobi == "SUCCESS":#火币买入交易成功

        logger.log("huobi buy success")

    else:
        logger.log("huobi buy error")

    flag_isHuobiBuyThreadInTrade = False

def bianBuy(quantity):#子线程执行的方法

    global flag_isBianBuyThreadInTrade
    #子线程执行币安买入
    orderResult_bian = ""
    orderResult_bian = account.order_bian_market("BUY",targetCoin,baseCoin,quantity)
    if orderResult_bian == "SUCCESS":#币安买入成功

        logger.log('bianbuy success')
    else:
        logger.log("bianbuy error")

    flag_isBianBuyThreadInTrade = False




#24小时重启一次
def enquireBian():

    try:
        URL_BIAN=websocket_endpoint_bian+'wx/%s%s@depth5' % (targetCoin.lower(),baseCoin.lower())
        ws_bian = DummyClient_bian(URL_BIAN,protocols=['http-only', 'chat'])
        #ws = DummyClient('ws://10.222.138.163:1889/websocket', protocols=['chat'])
        ws_bian.connect()
        ws_bian.run_forever()
    #except KeyboardInterrupt:
    except Exception,e:
        logger.log("enquireBian error")
        logger.log(e)
        ws_bian.close()


def enquireHuobi():

   #huobi
   while (1):
       try:
            #print 'enquireHuobi'
            #print websocket_endpoint_huobi
            ws_huobi = DummyClient_huobi(websocket_endpoint_huobi,protocols=['http-only', 'chat'])
            ws_huobi.connect()
            ws_huobi.run_forever()
            break

       except Exception,e:
            logger.log("huobi error")
            logger.log(e)
            try:
                ws_huobi.close()
            except Exception,e:

                logger.log("ws_huobi.close() error")
            time.sleep(10)
            logger.log("will retry connect huobi websocket")


def gzdecode(data) :
    compressedstream = StringIO.StringIO(data)
    gziper = gzip.GzipFile(fileobj=compressedstream)
    data2 = gziper.read()   # 读取解压缩后数据
    return data2

class DummyClient_huobi(WebSocketClient):


    def opened(self):

        print 'huobi opened'
        logger.log('huobi websocket opened')
        global flag_isHuobiSocketWork
        flag_isHuobiSocketWork=True
        tradeStr="""{"sub": "market.%s%s.depth.step0", "id": "id10"}""" % (targetCoin.lower(),baseCoin.lower())
        self.send(tradeStr)

    def closed(self, code, reason=None):

        logger.log("huobi websocket Closed down %s %s" %(code,reason))
        global flag_isHuobiSocketWork
        flag_isHuobiSocketWork=False
        time.sleep(180)
        enquireHuobi()


    def received_message(self, m):

        try:
            msg=gzdecode(m).decode('utf-8')
            global highestBuyNum_huobi
            global highestBuyPrice_huobi
            global lowestSellPrice_huobi
            global lowestSellNum_huobi
            global flag_isHuobiSocketWork

            if msg[:7] == '{"ping"':
                ts=msg[8:21]
                pong='{"pong":'+ts+'}'
                self.send(pong)
                tradeStr="""{"sub": "market.%s%s.depth.step0", "id": "id10"}""" % (targetCoin.lower(),baseCoin.lower())
                self.send(tradeStr)

            else:

                if msg[:5] == '{"ch"':

                    priceData=json.loads(msg)
                    #bids 买
                    highestBuyPrice_huobi=float(priceData['tick']['bids'][0][0])
                    highestBuyNum_huobi=float(priceData['tick']['bids'][0][1])
                    #asks 卖
                    #print priceData
                    lowestSellPrice_huobi=float(priceData['tick']['asks'][0][0])
                    lowestSellNum_huobi=float(priceData['tick']['asks'][0][1])
                    #if not flag_isHuobiSocketWork:flag_isHuobiSocketWork=True

        except Exception,e:


            logger.log("huobi on message error")
            logger.log(e)
            flag_isHuobiSocketWork=False



class DummyClient_bian(WebSocketClient):#bian


    def opened(self):

        print 'bian opened'
        logger.log('bian websocket opened')
        global flag_isBianSocketWork
        flag_isBianSocketWork=True

    def closed(self, code, reason=None):

        print "bian websocket Closed down", code, reason
        logger.log("bian websocket Closed down %s %s" %(code,reason))
        global flag_isBianSocketWork
        flag_isBianSocketWork=False
        time.sleep(180)
        enquireBian()

    def received_message(self, m):

        try:
            global highestBuyNum_bian
            global highestBuyPrice_bian
            global lowestSellPrice_bian
            global lowestSellNum_bian
            global flag_isBianSocketWork

            #if m.is_text:收到的是textMessage 格式
            recvStr = m.data.decode("utf-8")
            priceData = json.loads(recvStr)
            highestBuyPrice_bian=float(priceData["bids"][0][0])#最高买价
            highestBuyNum_bian=float(priceData["bids"][0][1])
            lowestSellPrice_bian=float(priceData["asks"][0][0])#最低卖价
            lowestSellNum_bian=float(priceData["asks"][0][1])
            #if not flag_isBianSocketWork:flag_isBianSocketWork=True
            #print lowestSellNum_bian
            #bids 买
            #asks 卖
        except Exception,e:


            logger.log("bian on message error")
            logger.log(e)
            flag_isBianSocketWork=False

def getZeroOflength(length):#获得0.000001指定位数

    str='0.'
    for i in range(0,length-1):

        str += '0'
    str += '1'
    number=float(str)
    return number

def getAccurateOfNumber(number):#获取小数点后的位数

    numberStr = str(number)
    if '.' in numberStr:
        indexOfPoint = numberStr.index('.')
        accurate=len(numberStr)-indexOfPoint-1
        return accurate

    else:
        return 0


def insertRateData(queryTime,rate1,rate2):

    logger.log("insertRateData")
    dao.insertRate(targetCoin,baseCoin,queryTime,rate1,rate2)



if __name__ == '__main__':

    print 'kyoto start'
    baseprice=0.00
    global highestBuyPrice_huobi
    global highestBuyNum_huobi
    global lowestSellPrice_huobi
    global lowestSellNum_huobi
    global highestBuyPrice_bian
    global highestBuyNum_bian
    global lowestSellPrice_bian
    global lowestSellNum_bian
    highestBuyPrice_huobi=0
    highestBuyNum_huobi=0
    lowestSellPrice_huobi=0
    lowestSellNum_huobi=0
    highestBuyPrice_bian=0
    highestBuyNum_bian=0
    lowestSellPrice_bian=0
    lowestSellNum_bian=0

    global flag_isHuobiSocketWork
    global flag_isBianSocketWork
    flag_isHuobiSocketWork=True
    flag_isBianSocketWork=True

    global flag_isHuobiInTrade
    global flag_isBianInTrade
    flag_isHuobiBuyThreadInTrade=False
    flag_isBianBuyThreadInTrade=False

    logNumber=0

    #context = ssl._create_unverified_context()
    #gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    #ssl._create_default_https_context = ssl._create_unverified_context
    dayOnStart = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    logger.log("start date: %s" % dayOnStart)

    coins=dao.queryCoins()
    logger.log("targetCoin: %s baseCoin %s" % (coins['targetCoin'],coins['baseCoin']))
    #print  "目标货币: %s 基础货币 %s" % (coins['targetCoin'],coins['baseCoin'])
    targetCoin = coins['targetCoin']
    baseCoin = coins['baseCoin']
    limitRate_huobiSell_bianBuy=coins['limitRate_huobiSell_bianBuy']
    limitRate_bianSell_huobiBuy=coins['limitRate_bianSell_huobiBuy']
    logger.log("tradelimit: huobiSell-bianBuy %f bianSell-huobiBuy %f" % (limitRate_huobiSell_bianBuy,limitRate_bianSell_huobiBuy))

    #获取当前账户余额，并写入数据库
    #kyoto的账户余额表有更新
    #table balance_normal
    balance_bian={}
    balance_huobi={}
    balance_bian=account.queryBalance_bian(targetCoin,baseCoin)
    balance_huobi=account.queryBalance_huobi(targetCoin,baseCoin)

    symbol=targetCoin+'/'+baseCoin

    if balance_bian and balance_huobi:

        logger.log("now balance information:")
        logger.log("huobi: %s %f  %s %f" % (targetCoin,balance_huobi[targetCoin],baseCoin,balance_huobi[baseCoin]))
        logger.log("bian: %s %f  %s %f" % (targetCoin,balance_bian[targetCoin],baseCoin,balance_bian[baseCoin]))

        dao.insertBalanceTable(targetCoin,baseCoin,balance_bian[targetCoin],balance_bian[baseCoin],balance_huobi[targetCoin],balance_huobi[baseCoin])
        #send information
        titleStr = "kyoto start"
        content1Str = "huobi:%sbalance%.8f%sbalance%.8f" % (targetCoin,balance_huobi[targetCoin],baseCoin,balance_huobi[baseCoin])
        content2Str = "bian:%sbalance%.8f%sbalance%.8f" % (targetCoin,balance_bian[targetCoin],baseCoin,balance_bian[baseCoin])
        remarkStr = time.strftime('%Y-%m-%d%H:%M:%S',time.localtime(time.time()))
        #notice.sendTextInfo(titleStr,content1Str,content2Str,remarkStr)

        websocket_endpoint_huobi=config.huobiRef['websocket_endpoint']
        websocket_endpoint_bian=config.binanceRef['websocket_endpoint']


        #开始socket连接，子线程启动

        threads = []
        t_huobi = threading.Thread(target=enquireHuobi)
        threads.append(t_huobi)
        t_bian = threading.Thread(target=enquireBian)
        threads.append(t_bian)

        for t in threads:

            t.setDaemon(True)
            t.start()

        acktime=datetime.datetime.now()
        old_rate_bianSell_huobiBuy=0.00
        old_rate_huobiSell_bianBuy=0.00
        while (1):

           if flag_isBianSocketWork and flag_isHuobiSocketWork:#socket正常工作状态

               #有效值

               if highestBuyPrice_huobi and highestBuyNum_huobi and lowestSellPrice_huobi and lowestSellNum_huobi and highestBuyPrice_bian and highestBuyNum_bian and lowestSellPrice_bian and lowestSellNum_bian:


                   if baseprice <= 0 and highestBuyPrice_huobi:

                        baseprice=highestBuyPrice_huobi
                        print 'baseprice update to %f' % baseprice
                        logger.log('baseprice update to %f' % baseprice)

                   #每天更新一次价格
                   dayNow = time.strftime('%Y-%m-%d',time.localtime(time.time()))
                   if dayNow > dayOnStart:

                       dayOnStart = dayNow
                       baseprice = highestBuyPrice_huobi

                       logger.log("date update to: %s" % dayOnStart)
                       logger.log("baseprice update to: %f" % baseprice)


                   #判断价格是否达到触发条件
                   grossRevenue_huobiSell_bianBuy = 0.00
                   grossRevenue_bianSell_huobiBuy = 0.00
                   grossRevenue_huobiSell_bianBuy = highestBuyPrice_huobi-lowestSellPrice_bian
                   grossRevenue_bianSell_huobiBuy = highestBuyPrice_bian-lowestSellPrice_huobi
                   cost_bianSell_huobiBuy = 0.00
                   cost_huobiSell_bianBuy = 0.00
                   cost_bianSell_huobiBuy = config.binanceRef['tradeCost']*highestBuyPrice_bian+config.huobiRef['tradeCost']*lowestSellPrice_huobi
                   cost_huobiSell_bianBuy = config.huobiRef['tradeCost']*highestBuyPrice_huobi+config.binanceRef['tradeCost']*lowestSellPrice_bian
                   profit_huobiSell_bianBuy = 0.00
                   profit_bianSell_huobiBuy = 0.00
                   #减去交易成本
                   profit_bianSell_huobiBuy = grossRevenue_bianSell_huobiBuy-cost_bianSell_huobiBuy
                   profit_huobiSell_bianBuy = grossRevenue_huobiSell_bianBuy-cost_huobiSell_bianBuy
                   profitRate_bianSell_huobiBuy = 0.00
                   profitRate_huobiSell_bianBuy = 0.00
                   profitRate_bianSell_huobiBuy = profit_bianSell_huobiBuy/baseprice*100
                   profitRate_huobiSell_bianBuy = profit_huobiSell_bianBuy/baseprice*100

                   if logNumber <= 20:
                       logger.log("*rate*%d*bianS_huobiB:%f*huobiS_bian:%f" % (logNumber,profitRate_bianSell_huobiBuy,profitRate_huobiSell_bianBuy))

                   logNumber += 1
                   #达到币安卖出火币买入条件

                   #ack心跳
                   ackNow_time=datetime.datetime.now()
                   if (ackNow_time-acktime).total_seconds() >= 300: #5分钟心跳一次

                       logger.log("*rate*bianS_huobiB:%f*huobiS_bian:%f" % (profitRate_bianSell_huobiBuy,profitRate_huobiSell_bianBuy))
                       acktime = datetime.datetime.now()


                   if profitRate_bianSell_huobiBuy >= limitRate_bianSell_huobiBuy:

                       if balance_bian[targetCoin] > config.minTradeNum[symbol]*2 and balance_huobi[baseCoin] > balance_bian[targetCoin]*lowestSellPrice_huobi*1.3:
                       #余额足够

                           #发起交易

                           quantity = 0.00#和最小tradeNum精度一致，xrp为整数
                           #最小tradeNum精度
                           minNumberLen=getAccurateOfNumber(config.minTradeNum[symbol])
                           quantity = min(highestBuyNum_bian,lowestSellNum_huobi,balance_bian[targetCoin])
                           if minNumberLen == 0:
                               quantity=int(quantity)
                           else:
                               quantity = quantity-getZeroOflength(minNumberLen)#先减去，防止四舍五入后不够
                               quantity = round(quantity,minNumberLen)

                           #quantity = 1

                           buybase=0.00
                           buybase=round(quantity*lowestSellPrice_huobi*1.002,5)
                           #logger.log("huobi buybase %f " % buybase)
                           #子线程执行火币买入
                           flag_isHuobiBuyThreadInTrade = True
                           #注意quantity=要买的baseCoin数量
                           time1 = datetime.datetime.now()
                           thread__huobiBuy = threading.Thread(target=huobiBuy,args=(buybase,))
                           thread__huobiBuy.setDaemon(True)
                           thread__huobiBuy.start()
                           #主线程执行币安卖出
                           orderResult_bian = ""
                           orderResult_bian = account.order_bian_market("SELL",targetCoin,baseCoin,quantity)
                           if orderResult_bian == "SUCCESS":#币安卖出成功

                                logger.log('bianSell success')
                           else:
                                logger.log("bianSell error")


                           #等待火币买入子线程的结果
                           while (1):

                               if not flag_isHuobiBuyThreadInTrade:break
                           time2 = datetime.datetime.now()
                           logger.log('use: %f microseconds' % (time2-time1).microseconds)
                           logger.log("trade group finish")

                           #审计结果

                           balance_new = checkTradeResult(targetCoin,baseCoin,balance_huobi,balance_bian,baseprice,quantity)
                           #更新余额
                           balance_bian=balance_new['balance_bian_new']
                           balance_huobi=balance_new['balance_huobi_new']
                           logger.log("trade result:")
                           logger.log("huobi: %s %f  %s %f" % (targetCoin,balance_huobi[targetCoin],baseCoin,balance_huobi[baseCoin]))
                           logger.log("bian: %s %f  %s %f" % (targetCoin,balance_bian[targetCoin],baseCoin,balance_bian[baseCoin]))


                       else:

                           #print 'bianSell huobiBuy can work,but balance is not enough'
                           pass



                   #达到火币卖出币安买入条件
                   elif profitRate_huobiSell_bianBuy >= limitRate_huobiSell_bianBuy:

                       if balance_huobi[targetCoin] > config.minTradeNum[symbol]*2 and balance_bian[baseCoin] > balance_huobi[targetCoin]*lowestSellPrice_bian*1.3:
                       #余额足够
                           #发起交易
                           quantity = 0.00#和最小tradeNum精度一致，xrp为整数
                           #最小tradeNum精度
                           minNumberLen=getAccurateOfNumber(config.minTradeNum[symbol])
                           quantity = min(highestBuyNum_huobi,lowestSellNum_bian,balance_huobi[targetCoin])
                           if minNumberLen == 0:
                               quantitySell=int(quantity)
                               quantityBuy=int(quantity*1.002)

                           else:
                               quantity = quantity-getZeroOflength(minNumberLen)#先减去，防止四舍五入后不够
                               quantitySell = round(quantity,minNumberLen)
                               quantityBuy = round(quantity*1.002,minNumberLen)

                         

                           #子线程执行币安买入
                           flag_isBianBuyThreadInTrade = True

                           time3 = datetime.datetime.now()
                           thread__bianBuy = threading.Thread(target=bianBuy,args=(quantityBuy,))
                           thread__bianBuy.setDaemon(True)
                           thread__bianBuy.start()


                           #主线程执行火币卖出
                           orderResult_huobi = ""
                           orderResult_huobi = account.order_huobi_market("SELL",targetCoin.lower(),baseCoin.lower(),quantitySell)
                           if orderResult_huobi == "SUCCESS":#火币卖出成功

                                logger.log('huobi Sell success')
                           else:
                                logger.log("huobi Sell error")

                           #等待币安买入子线程的结果
                           while (1):

                               if not flag_isBianBuyThreadInTrade:break

                           time4 = datetime.datetime.now()
                           logger.log('use: %f microseconds' % (time4-time3).microseconds)
                           logger.log("trade group finish")

                           balance_new = checkTradeResult(targetCoin,baseCoin,balance_huobi,balance_bian,baseprice,quantity)
                           #更新余额
                           balance_bian=balance_new['balance_bian_new']
                           balance_huobi=balance_new['balance_huobi_new']
                           logger.log("trade result:")
                           logger.log("huobi: %s %f  %s %f" % (targetCoin,balance_huobi[targetCoin],baseCoin,balance_huobi[baseCoin]))
                           logger.log("bian: %s %f  %s %f" % (targetCoin,balance_bian[targetCoin],baseCoin,balance_bian[baseCoin]))


                   #保存价格信息
                   #profitRate_huobiSell_bianBuy
                   #profitRate_bianSell_huobiBuy
                   #存在一个收益率>0时
                   if profitRate_huobiSell_bianBuy>0.5 or profitRate_bianSell_huobiBuy>0:

                       if old_rate_bianSell_huobiBuy<>profitRate_bianSell_huobiBuy or old_rate_huobiSell_bianBuy<>profitRate_huobiSell_bianBuy:
                       #保存不同的值

                          timeStr=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

                          old_rate_bianSell_huobiBuy=profitRate_bianSell_huobiBuy
                          old_rate_huobiSell_bianBuy=profitRate_huobiSell_bianBuy
                          thread_save = threading.Thread(target=insertRateData,args=(timeStr,profitRate_huobiSell_bianBuy,profitRate_bianSell_huobiBuy,))
                          thread_save.setDaemon(True)
                          thread_save.start()

    else:

        print '任务开始，查询账户余额错误'
        logger.log("when task start,enquire balance error")



