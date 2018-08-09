
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

#24小时重启一次
def enquireBianPrice():

    while (1):
        try:
            URL_BIAN=myConfig.binanceRef['websocket_endpoint']+'wx/%s%s@depth5' % (targetCoin.lower(),baseCoin.lower())
            ws_bian = DummyClient_bian(URL_BIAN,protocols=['http-only', 'chat'])
            #ws = DummyClient('ws://10.222.138.163:1889/websocket', protocols=['chat'])
            ws_bian.connect()
            ws_bian.run_forever()
            break
            #except KeyboardInterrupt:
        except Exception,e:

            print "huobi websocket error"
            myLogger.log("bian websocket error")
            try:
                ws_bian.close()
            except Exception,e:

                print("ws_bian.close() error")
                myLogger.log("ws_bian.close() error")
                myLogger.log(e)
            time.sleep(10)
            print("will retry connect bian websocket")
            myLogger.log("will retry connect bian websocket")



class DummyClient_bian(WebSocketClient):#bian


    def opened(self):

        print 'bian websocket opened'
        myLogger.log('bian websocket opened')
        global flag_isBianSocketWork
        flag_isBianSocketWork=True

    def closed(self, code, reason=None):

        print "bian websocket Closed down", code, reason
        myLogger.log("bian websocket Closed down %s %s" %(code,reason))
        global flag_isBianSocketWork
        flag_isBianSocketWork=False
        time.sleep(180)
        enquireBianPrice()

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
            #print "币安最低卖价: %f"% lowestSellPrice_bian
            #bids 买
            #asks 卖
        except Exception,e:


            myLogger.log("bian on message error")
            myLogger.log(e)
            flag_isBianSocketWork=False



def enquireHuobiPrice():

    while (1):
       try:
            #print 'enquireHuobi'
            myLogger.log('websocket_endpoint_huobi start to connect')
            ws_huobi = DummyClient_huobi(myConfig.huobiRef['websocket_endpoint'],protocols=['http-only', 'chat'])
            ws_huobi.connect()
            ws_huobi.run_forever()
            break

       except Exception,e:

            print "huobi websocket error"
            myLogger.log("huobi websocket error")
            myLogger.log(e)
            try:
                ws_huobi.close()
            except Exception,e:

                print("ws_huobi.close() error")
                myLogger.log("ws_huobi.close() error")
                myLogger.log(e)
            time.sleep(10)
            print("will retry connect huobi websocket")
            myLogger.log("will retry connect huobi websocket")


def gzdecode(data) :
    compressedstream = StringIO.StringIO(data)
    gziper = gzip.GzipFile(fileobj=compressedstream)
    data2 = gziper.read()   # 读取解压缩后数据
    return data2


class DummyClient_huobi(WebSocketClient):


    def opened(self):

        print('huobi websocket opened')
        myLogger.log('huobi websocket opened')
        global flag_isHuobiSocketWork
        flag_isHuobiSocketWork=True
        tradeStr="""{"sub": "market.%s%s.depth.step0", "id": "id10"}""" % (targetCoin.lower(),baseCoin.lower())
        self.send(tradeStr)

    def closed(self, code, reason=None):

        print("huobi websocket Closed down %s %s" %(code,reason))
        myLogger.log("huobi websocket Closed down %s %s" %(code,reason))
        global flag_isHuobiSocketWork
        flag_isHuobiSocketWork=False
        time.sleep(180)
        enquireHuobiPrice()


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
                    #价格显示出来核对下
                    #print "火币的最低卖价: "+"%f" % lowestSellPrice_huobi
                    #print "火币的最低卖价深度: "+"%f" % lowestSellNum_huobi

        except Exception,e:


            print("huobi on message error")
            myLogger.log("huobi on message error")
            print(e)
            flag_isHuobiSocketWork=False

targetCoin=''
baseCoin=''
baseprice=0.00


if __name__ == '__main__':

    global flag_isHuobiSocketWork
    global flag_isBianSocketWork
    flag_isHuobiSocketWork=True
    flag_isBianSocketWork=True


    global highestBuyNum_huobi
    global highestBuyPrice_huobi
    global lowestSellPrice_huobi
    global lowestSellNum_huobi
    highestBuyNum_huobi=0
    highestBuyPrice_huobi=0
    lowestSellPrice_huobi=0
    lowestSellNum_huobi=0

    global highestBuyNum_bian
    global highestBuyPrice_bian
    global lowestSellPrice_bian
    global lowestSellNum_bian
    highestBuyNum_bian=0
    highestBuyPrice_bian=0
    lowestSellPrice_bian=0
    lowestSellNum_bian=0

    dayOnStart = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    minTradeNumOfTargetCoin=0
    for key in myConfig.minNumOfLimitTrade:

        targetCoin=key.split('/')[0]
        baseCoin=key.split('/')[1]

        minTradeNumOfTargetCoin=myConfig.minNumOfLimitTrade[key]
    symbol=targetCoin+baseCoin
    balance_bian={}
    balance_huobi={}

    balance_bian=myAccount.queryBalance_bian(targetCoin,baseCoin)
    balance_huobi=myAccount.queryBalance_huobi(targetCoin,baseCoin)


    if balance_bian and balance_huobi:

        myLogger.log("now balance information:")
        myLogger.log("huobi: %s %s  %s %s" % (targetCoin,balance_huobi[targetCoin],baseCoin,balance_huobi[baseCoin]))
        myLogger.log("bian: %s %s  %s %s" % (targetCoin,balance_bian[targetCoin],baseCoin,balance_bian[baseCoin]))

        title="now balance information:"
        content1="huobi: %s %s  %s %s" % (targetCoin,balance_huobi[targetCoin],baseCoin,balance_huobi[baseCoin])
        content2="bian: %s %s  %s %s" % (targetCoin,balance_bian[targetCoin],baseCoin,balance_bian[baseCoin])
        remark="fukuoka"
        notice.sendTextInfo(title,content1,content2,remark)


    threads = []
    t_huobi = threading.Thread(target=enquireHuobiPrice)
    threads.append(t_huobi)
    t_bian = threading.Thread(target=enquireBianPrice)
    threads.append(t_bian)
    for t in threads:

        t.setDaemon(True)
        t.start()

    acktime=datetime.datetime.now()
    oldRate_huobiSell_bianBuy=0
    oldRate_bianSell_huobiBuy=0
    while (1):

        if flag_isBianSocketWork and flag_isHuobiSocketWork:#socket正常工作状态

            if highestBuyPrice_huobi and highestBuyNum_huobi and lowestSellPrice_huobi and lowestSellNum_huobi and highestBuyPrice_bian and highestBuyNum_bian and lowestSellPrice_bian and lowestSellNum_bian:

                if baseprice <= 0 and highestBuyPrice_huobi:

                        baseprice=highestBuyPrice_huobi
                        

                #每天更新一次价格
                dayNow = time.strftime('%Y-%m-%d',time.localtime(time.time()))
                if dayNow > dayOnStart:

                    dayOnStart = dayNow
                    baseprice = highestBuyPrice_huobi

                    title="baseprice update:"
                    content1="date update to: %s" % dayOnStart
                    content2="baseprice update to: %f" % baseprice
                    remark="fukuoka"
                    notice.sendTextInfo(title,content1,content2,remark)

                #判断价格是否达到触发条件
                #这里不能直接使用价格信息，避免数据在同时被修改
                tmp_lowestSellPrice_bian=lowestSellPrice_bian
                tmp_highestBuyPrice_bian=highestBuyPrice_bian
                tmp_lowestSellPrice_huobi=lowestSellPrice_huobi
                tmp_highestBuyPrice_huobi=highestBuyPrice_huobi

                tmp_lowestSellNum_bian=lowestSellNum_bian
                tmp_highestBuyNum_bian=highestBuyNum_bian
                tmp_lowestSellNum_huobi=lowestSellNum_huobi
                tmp_highestBuyNum_huobi=highestBuyNum_huobi



                grossRevenue_huobiSell_bianBuy = tmp_highestBuyPrice_huobi-tmp_lowestSellPrice_bian
                grossRevenue_bianSell_huobiBuy = tmp_highestBuyPrice_bian-tmp_lowestSellPrice_huobi
                cost_bianSell_huobiBuy = myConfig.binanceRef['tradeCost']*tmp_highestBuyPrice_bian+myConfig.huobiRef['tradeCost']*tmp_lowestSellPrice_huobi
                cost_huobiSell_bianBuy = myConfig.huobiRef['tradeCost']*tmp_highestBuyPrice_huobi+myConfig.binanceRef['tradeCost']*tmp_lowestSellPrice_bian

                #减去交易成本
                profit_bianSell_huobiBuy = grossRevenue_bianSell_huobiBuy-cost_bianSell_huobiBuy
                profit_huobiSell_bianBuy = grossRevenue_huobiSell_bianBuy-cost_huobiSell_bianBuy
                profitRate_bianSell_huobiBuy = profit_bianSell_huobiBuy/baseprice*100
                profitRate_huobiSell_bianBuy = profit_huobiSell_bianBuy/baseprice*100


                #ack心跳
                ackNow_time=datetime.datetime.now()
                if (ackNow_time-acktime).total_seconds() >= 1200: #5分钟心跳一次

                    myLogger.log("ACKTRADE*bianSell_huobiBuy:%f*huobiSell_bianBuy:%f" % (profitRate_bianSell_huobiBuy,profitRate_huobiSell_bianBuy))
                    acktime = datetime.datetime.now()

                if (oldRate_huobiSell_bianBuy<>profitRate_huobiSell_bianBuy or oldRate_bianSell_huobiBuy<>profitRate_bianSell_huobiBuy):

                        print("ACKTRADE*bianSell_huobiBuy:%f*huobiSell_bianBuy:%f" % (profitRate_bianSell_huobiBuy,profitRate_huobiSell_bianBuy))

                #达到币安卖出火币买入条件
                if profitRate_bianSell_huobiBuy > 0.2:

                    #防止重复打印log
                    if (oldRate_huobiSell_bianBuy<>profitRate_huobiSell_bianBuy or oldRate_bianSell_huobiBuy<>profitRate_bianSell_huobiBuy):

                        myLogger.log("reachTradeCondition*bianSell_huobiBuy:%f*huobiSell_bianBuy:%f" % (profitRate_bianSell_huobiBuy,profitRate_huobiSell_bianBuy))

                    #判断进入机会，卖出价格不能偏离成本价格太多
                    if tmp_highestBuyPrice_bian < myConfig.orderLimit[symbol]['costPrice']*(1-myConfig.orderLimit[symbol]['offset']):

                        #卖出价格太低，不进行交易
                        #防止重复打印log
                        if (oldRate_huobiSell_bianBuy<>profitRate_huobiSell_bianBuy or oldRate_bianSell_huobiBuy<>profitRate_bianSell_huobiBuy):

                            myLogger.log("%f is too lower, stop order" % tmp_highestBuyPrice_bian)

                        continue

                    #判断对应的余额够不够
                    targetCoinQuantityToSell = 0
                    targetCoinSellPrice=0
                    targetCoinQuantityToBuy = 0
                    targetCoinBuyPrice=0
                    if balance_bian[targetCoin] > minTradeNumOfTargetCoin:
                        #另一侧账户baseCoin买入资金够不够?
                        if balance_huobi[baseCoin] > balance_bian[targetCoin]*tmp_lowestSellPrice_huobi*1.003:


                            targetCoinQuantityToSell = min(tmp_highestBuyNum_bian,tmp_lowestSellNum_huobi,balance_bian[targetCoin])
                            #bian 有最低 0.01 ETH的数量限制
                            if targetCoinQuantityToSell < minTradeNumOfTargetCoin:
                                if (oldRate_huobiSell_bianBuy<>profitRate_huobiSell_bianBuy or oldRate_bianSell_huobiBuy<>profitRate_bianSell_huobiBuy):
                                    myLogger.log("targetCoinQuantityToSell < minTradeNumOfTargetCoin")
                                continue

                            targetCoinQuantityToSell = targetCoinQuantityToSell-0.01
                            targetCoinQuantityToSell = round(targetCoinQuantityToSell,2)
                            targetCoinSellPrice=tmp_highestBuyPrice_bian-0.000001
                            targetCoinSellPrice = round(targetCoinSellPrice,6)

                            targetCoinQuantityToBuy = targetCoinQuantityToSell/0.998
                            targetCoinQuantityToBuy = round(targetCoinQuantityToBuy,5)
                            targetCoinBuyPrice=tmp_lowestSellPrice_huobi+0.000001
                            targetCoinBuyPrice = round(targetCoinBuyPrice,6)

                            #bian是FOK订单，不存在挂单可能
                            orderResult_bian=myAccount.order_bian("SELL",targetCoin,baseCoin,targetCoinQuantityToSell,targetCoinSellPrice)
                            if orderResult_bian == "SUCCESS":#币安卖出成功

                                myLogger.log('bianSell success')
                                #火币买入
                                orderResult_huobi=myAccount.order_huobi("BUY",targetCoin.lower(),baseCoin.lower(),targetCoinQuantityToBuy,targetCoinBuyPrice)

                                if orderResult_huobi:#结果不为空

                                    if orderResult_huobi['status'] == "ok":#火币买入成功

                                        #!注意可能是处于挂单状态，需要查询一下进一步的交易状态
                                        orderId=orderResult_huobi['data']
                                        myLogger.log('will query huobi orderId:'+orderId)
                                        while (1):

                                            tradeDetail=myAccount.getTradeDetail_huobi(orderId)
                                            if tradeDetail:

                                                if tradeDetail['data']['state'] != "filled":#没有完成交易

                                                    myLogger.log("order of huobi is not finished")

                                                else:#交易全部完成 state = filled

                                                    myLogger.log("order of huobi is finished")
                                                    title="bianSell_huobiBuy success:"
                                                    content1="Sell: %s %s" % (targetCoinQuantityToSell,targetCoinSellPrice)
                                                    content2="Buy: %s %s" % (targetCoinQuantityToBuy,targetCoinBuyPrice)
                                                    remark="fukuoka"
                                                    notice.sendTextInfo(title,content1,content2,remark)

                                                    #更新balance
                                                    balance_bian=myAccount.queryBalance_bian(targetCoin,baseCoin)
                                                    balance_huobi=myAccount.queryBalance_huobi(targetCoin,baseCoin)


                                                    myLogger.log("update balance information:")
                                                    myLogger.log("huobi: %s %s  %s %s" % (targetCoin,balance_huobi[targetCoin],baseCoin,balance_huobi[baseCoin]))
                                                    myLogger.log("bian: %s %s  %s %s" % (targetCoin,balance_bian[targetCoin],baseCoin,balance_bian[baseCoin]))

                                                    title="update balance information:"
                                                    content1="huobi: %s %s  %s %s" % (targetCoin,balance_huobi[targetCoin],baseCoin,balance_huobi[baseCoin])
                                                    content2="bian: %s %s  %s %s" % (targetCoin,balance_bian[targetCoin],baseCoin,balance_bian[baseCoin])
                                                    remark="fukuoka"
                                                    notice.sendTextInfo(title,content1,content2,remark)

                                                    break#不再继续查询交易结果



                                            else:

                                                myLogger.log("get trade detail huobi is null")

                                            time.sleep(3)



                                    else:#火币没有买入成功 status 不是 ok

                                        myLogger.log('火币没有买入成功，停止程序')
                                        break
                                else:

                                    myLogger.log("this is something woring in huobi trade")
                                    break



                            else:
                                myLogger.log("bianSell error")



                        else:
                            if (oldRate_huobiSell_bianBuy<>profitRate_huobiSell_bianBuy or oldRate_bianSell_huobiBuy<>profitRate_bianSell_huobiBuy):

                                myLogger.log('baseCoin to buy of huobi is not enough')

                    else:

                        #防止重复打印log
                        if (oldRate_huobiSell_bianBuy<>profitRate_huobiSell_bianBuy or oldRate_bianSell_huobiBuy<>profitRate_bianSell_huobiBuy):

                            myLogger.log('targetCoin to sell of bian is not enough')
                    #先发起交易



                #达到火币卖出币安买入条件
                elif profitRate_huobiSell_bianBuy > 0.5:
                    #防止重复打印log
                    if (oldRate_huobiSell_bianBuy<>profitRate_huobiSell_bianBuy or oldRate_bianSell_huobiBuy<>profitRate_bianSell_huobiBuy):

                        myLogger.log("reachTradeCondition*bianSell_huobiBuy:%f*huobiSell_bianBuy:%f" % (profitRate_bianSell_huobiBuy,profitRate_huobiSell_bianBuy))


                    #判断进入机会，卖出价格不能偏离成本价格太多
                    if tmp_highestBuyPrice_huobi < myConfig.orderLimit[symbol]['costPrice']*(1-myConfig.orderLimit[symbol]['offset']):

                        #卖出价格太低，不进行交易
                        #防止重复打印log
                        if (oldRate_huobiSell_bianBuy<>profitRate_huobiSell_bianBuy or oldRate_bianSell_huobiBuy<>profitRate_bianSell_huobiBuy):

                            myLogger.log("%f is too lower, stop order" % tmp_highestBuyPrice_huobi)

                        continue




                    targetCoinQuantityToSell = 0
                    targetCoinSellPrice=0
                    targetCoinQuantityToBuy = 0
                    targetCoinBuyPrice=0
                    flag_tradeGo=True
                    if balance_huobi[targetCoin] > minTradeNumOfTargetCoin:


                        #另一侧账户baseCoin买入资金够不够?
                        if balance_bian[baseCoin] > balance_huobi[targetCoin]*tmp_lowestSellPrice_bian*1.003:


                            targetCoinQuantityToSell = min(tmp_highestBuyNum_huobi,tmp_lowestSellNum_bian,balance_huobi[targetCoin])
                            #bian 有最低 0.01 ETH的数量限制
                            if targetCoinQuantityToSell < minTradeNumOfTargetCoin:
                                if (oldRate_huobiSell_bianBuy<>profitRate_huobiSell_bianBuy or oldRate_bianSell_huobiBuy<>profitRate_bianSell_huobiBuy):
                                    myLogger.log("targetCoinQuantityToSell < minTradeNumOfTargetCoin")
                                continue

                            targetCoinQuantityToSell = targetCoinQuantityToSell-0.01
                            targetCoinQuantityToSell = round(targetCoinQuantityToSell,2)
                            targetCoinSellPrice=tmp_highestBuyPrice_huobi-0.000001
                            targetCoinSellPrice = round(targetCoinSellPrice,6)

                            targetCoinQuantityToBuy = targetCoinQuantityToSell/0.998
                            targetCoinQuantityToBuy = round(targetCoinQuantityToBuy,5)
                            targetCoinBuyPrice=tmp_lowestSellPrice_bian+0.000001
                            targetCoinBuyPrice = round(targetCoinBuyPrice,6)

                            orderResult_huobi=myAccount.order_huobi("SELL",targetCoin.lower(),baseCoin.lower(),targetCoinQuantityToSell,targetCoinSellPrice)
                            if orderResult_huobi:

                                 if orderResult_huobi['status'] == "ok":#火币卖出成功

                                    #有可能挂单，需要进行查询
                                    orderId=orderResult_huobi['data']
                                    myLogger.log('will query huobi orderId:'+orderId)
                                    while (1):#查询火币交易结果

                                        tradeDetail=myAccount.getTradeDetail_huobi(orderId)
                                        if tradeDetail:

                                            if tradeDetail['data']['state'] != "filled":#没有完成交易
                                                flag_tradeGo=False#停止交易
                                                myLogger.log("order of huobi is not finished")
                                                #要撤销交易
                                                cancelResult=myAccount.submitcancel_huobi(orderId)
                                                if cancelResult:

                                                        if cancelResult['status'] == 'ok':#撤销火币交易成功

                                                            myLogger.log("cancel order of huobi success")

                                                        else:
                                                            myLogger.log("cancel order of huobi wrong")

                                                else:#撤销交易没有结果

                                                    myLogger.log("cancel order of huobi wrong")
                                                break

                                            else:#交易全部完成 state = filled

                                                myLogger.log("order of huobi is finished")
                                                #币安买入交易

                                                break

                                        else:#查询火币交易结果为空

                                            myLogger.log("get trade detail of huobi is null")

                                        time.sleep(2)



                                    #币安买入交易
                                    if flag_tradeGo:
                                        myLogger.log("bian trade start")
                                        orderResult=myAccount.order_bian("BUY",targetCoin,baseCoin,targetCoinQuantityToBuy,targetCoinBuyPrice)
                                        if orderResult:

                                            if orderResult['status'] != 'FILLED':#挂单 NEW

                                                myLogger.log("bian trade result is new,not finished")
                                                symbol=""+targetCoin+baseCoin
                                                myLogger.log("bian symbol:"+symbol)
                                                orderId=orderResult['orderId']
                                                myLogger.log("bian orderId:"+orderId)
                                                while (1):#循环查询币安交易结果

                                                    tradeDetailResult=myAccount.getTradeDetail_bian(symbol,orderId)
                                                    if tradeDetailResult:

                                                        if tradeDetailResult['status'] == "FILLED":

                                                            myLogger.log("bian trade is success in query detail cricle")
                                                            break

                                                    time.sleep(3)


                                            #币安交易成功 FILLED
                                            title="huobiSell_bianBuy success:"
                                            content1="Sell: %s %s" % (targetCoinQuantityToSell,targetCoinSellPrice)
                                            content2="Buy: %s %s" % (targetCoinQuantityToBuy,targetCoinBuyPrice)
                                            remark="fukuoka"
                                            notice.sendTextInfo(title,content1,content2,remark)


                                            #更新balance
                                            balance_bian=myAccount.queryBalance_bian(targetCoin,baseCoin)
                                            balance_huobi=myAccount.queryBalance_huobi(targetCoin,baseCoin)


                                            myLogger.log("update balance information:")
                                            myLogger.log("huobi: %s %s  %s %s" % (targetCoin,balance_huobi[targetCoin],baseCoin,balance_huobi[baseCoin]))
                                            myLogger.log("bian: %s %s  %s %s" % (targetCoin,balance_bian[targetCoin],baseCoin,balance_bian[baseCoin]))

                                            title="update balance information:"
                                            content1="huobi: %s %s  %s %s" % (targetCoin,balance_huobi[targetCoin],baseCoin,balance_huobi[baseCoin])
                                            content2="bian: %s %s  %s %s" % (targetCoin,balance_bian[targetCoin],baseCoin,balance_bian[baseCoin])
                                            remark="fukuoka"
                                            notice.sendTextInfo(title,content1,content2,remark)



                                        else:
                                            myLogger.log("bian trade result is null")

                                    else:

                                        myLogger.log("bian trade will not contine becase flag is down")


                                 else:
                                    myLogger.log("this is something woring in huobi trade")

                            else:#火币交易结果为空

                                 myLogger.log("this is something woring in huobi trade")

                        else:
                            #防止重复打印log
                            if (oldRate_huobiSell_bianBuy<>profitRate_huobiSell_bianBuy or oldRate_bianSell_huobiBuy<>profitRate_bianSell_huobiBuy):

                                myLogger.log('baseCoin to buy of bian is not enough')

                    else:

                        if (oldRate_huobiSell_bianBuy<>profitRate_huobiSell_bianBuy or oldRate_bianSell_huobiBuy<>profitRate_bianSell_huobiBuy):

                            myLogger.log('targetCoin to sell of huobi is not enough')


                else:#既没有达到币安卖出火币买入条件，也没有达到另外一边的条件
                    pass
                    #print "%f %f" %(profitRate_bianSell_huobiBuy,profitRate_huobiSell_bianBuy)

                oldRate_huobiSell_bianBuy=profitRate_huobiSell_bianBuy
                oldRate_bianSell_huobiBuy=profitRate_bianSell_huobiBuy

        else:#'one websocket is wrong'

            pass


