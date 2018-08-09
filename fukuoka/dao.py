#coding=utf-8
#!/usr/bin/python
import mysql.connector
import socket
import myLogger

def getTradeLimit(symbol):

    tradeLimit={}
    pwd='MyNewPass4!'
    db = mysql.connector.connect(user='root', password=pwd, database='coin', use_unicode=True)
    cursor = db.cursor()

    # SQL 查询语句
    sql = "SELECT * FROM tradeLimit where symbol='%s'" % symbol
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchone()
        tradeLimit['bianSell_huobiBuy']=float(results[2])
        tradeLimit['huobiSell_bianBuy']=float(results[3])
        return tradeLimit

    except Exception,e:

        print e
        myLogger.log("get trade limit error")
        myLogger.log(e)

    # 关闭数据库连接
    db.close()



def getSymbols():
    symbols=[]
    pwd='MyNewPass4!'

    db = mysql.connector.connect(user='root', password=pwd, database='coin', use_unicode=True)
    cursor = db.cursor()

    # SQL 查询语句
    sql = "SELECT * FROM symbols where usable>=100"
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        for row in results:

            baseCoin=""
            targetCoin=""
            if row[1].endswith('usdt'):

                baseCoin='usdt'
            elif row[1].endswith('btc'):

                baseCoin='btc'
            elif row[1].endswith('eth'):

                baseCoin='eth'
            else:
                print 'get symbols error'

            index=row[1].index(baseCoin)
            targetCoin=row[1][:index]
            symbol = targetCoin.upper()+"/"+baseCoin.upper()
            symbols.append(symbol)

    except Exception,e:

        print e

    # 关闭数据库连接
    db.close()

    return symbols


def saveSymbol(symbol):

    pwd='MyNewPass4!'
    db = mysql.connector.connect(user='root', password=pwd, database='coin', use_unicode=True)
    cursor = db.cursor()
    #默认0不可用
    sql = "insert into symbols (symbol,usable) values ('%s','%d')" % (symbol,0)
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
        print 'save symbol:%s' % symbol

    except Exception,e:
        print e
        db.rollback()


    # 关闭数据库连接
    db.close()

def insertQueryPriceData(targetCoin,baseCoin,queryTime,rate_bianSell_huobiBuy,rate_huobiSell_bianBuy,
                         lowestSellPrice_huobi,highestBuyPrice_huobi,
                         lowestSellNum_huobi,highestBuyNum_huobi,
                         lowestSellPrice_bian,highestBuyPrice_bian,
                         lowestSellNum_bian,highestBuyNum_bian):

    pwd='MyNewPass4!'
    db = mysql.connector.connect(user='root', password=pwd, database='coin', use_unicode=True)
    cursor = db.cursor()
    symbol ="%s%s" % (targetCoin,baseCoin)
    sql = "insert into priceData (queryTime,rate_bianSell_huobiBuy,rate_huobiSell_bianBuy," \
          "lowestSellPrice_huobi,highestBuyPrice_huobi,lowestSellNum_huobi,highestBuyNum_huobi," \
          "lowestSellPrice_bian,highestBuyPrice_bian,lowestSellNum_bian,highestBuyNum_bian,symbol) " \
          "values ('%s','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%s')"\
          % (queryTime,rate_bianSell_huobiBuy,rate_huobiSell_bianBuy,
             lowestSellPrice_huobi,highestBuyPrice_huobi,
             lowestSellNum_huobi,highestBuyNum_huobi,
             lowestSellPrice_bian,highestBuyPrice_bian,
             lowestSellNum_bian,highestBuyNum_bian,symbol)
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
        print 'insert price data %s' % symbol


    except Exception,e:
        print e
        db.rollback()


    # 关闭数据库连接
    db.close()


def insertActualPriceData(queryTime,symbol,direction,rate,sellMarketNumber,buyMarketNumber):

    myLogger.log('def insertActualPriceData')
    pwd='MyNewPass4!'
    db = mysql.connector.connect(user='root', password=pwd, database='coin', use_unicode=True)
    cursor = db.cursor()

    sql = "insert into actualPriceRecord (queryTime,symbol,tradeDirection,tradeRate,sellMarketNumber," \
          "buyMarketNumber) values ('%s','%s','%s','%f','%f','%f')"\
          % (queryTime,symbol,direction,rate,sellMarketNumber,buyMarketNumber)

    myLogger.log(sql)
    try:
        # 执行SQL语句
        myLogger.log("try insert")
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
        myLogger.log("finish insert")
      


    except Exception,e:
        print e
        myLogger.log("insert actual price error")
        myLogger.log(e)
        db.rollback()


    # 关闭数据库连接
    db.close()

#需要修改
def insertRate(targetCoin,baseCoin,queryTime,rate_bianSell_huobiBuy,rate_huobiSell_bianBuy):

    pwd='MyNewPass4!'
    db = mysql.connector.connect(user='root', password=pwd, database='coin', use_unicode=True)
    cursor = db.cursor()

    tableName="rateRecord_%s%s" % (targetCoin.lower(),baseCoin.lower())
    #print tableName
    sql = "insert into %s (queryTime,rate_bianSell_huobiBuy,rate_huobiSell_bianBuy) values ('%s','%f','%f')" % (tableName,queryTime,rate_bianSell_huobiBuy,rate_huobiSell_bianBuy)
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
        #print "insert rate finish"
        #logger.log("insert rate finish")

    except Exception,e:
        print e
        db.rollback()
        #print "insert rate error"
        #print e


    # 关闭数据库连接
    db.close()


if __name__ == '__main__':

    #insertRate('ETH','USDT','2018-01-25 12:23:19',-0.15,-0.16)
    #print getSymbols(10,10)
    print getTradeLimit('STEEMETH')