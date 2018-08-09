#coding=utf-8
#!/usr/bin/python
import logger
import mysql.connector
import socket

def insertRate(targetCoin,baseCoin,queryTime,rate1,rate2):

    pwd=""
    if 'macbook' in socket.getfqdn(socket.gethostname()):pwd='root'
    else:pwd='Zhuwenin841002*'
    db = mysql.connector.connect(user='root', password=pwd, database='coin', use_unicode=True)
    cursor = db.cursor()
    # SQL 查询语句
    #rateRecord_xrpbtc_huobi_bian
    tableName="rateRecord_%s%s_huobi_bian" % (targetCoin.lower(),baseCoin.lower())
    #print tableName
    sql = "insert into %s (queryTime,rate_huobiSell_bianBuy,rate_bianSell_huobiBuy) values ('%s','%f','%f')" % (tableName,queryTime,rate1,rate2)
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
        #print "insert rate finish"
        #logger.log("insert rate finish")

    except Exception,e:
        db.rollback()
        #print "insert rate error"
        #print e
        logger.log("insert rate data error")
        logger.log(e)

    # 关闭数据库连接
    db.close()


def queryCoins():

    coins={}
    pwd=""
    if 'macbook' in socket.getfqdn(socket.gethostname()):pwd='root'
    else:pwd='Zhuwenin841002*'

    db = mysql.connector.connect(user='root', password=pwd, database='coin', use_unicode=True)
    cursor = db.cursor()

    # SQL 查询语句
    sql = "SELECT * FROM tradeCoins order by id desc"
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        for row in results:

            #print row[1]
            coins['targetCoin']=row[1]
            coins['baseCoin']=row[2]
            coins['limitRate_huobiSell_bianBuy']=row[3]
            coins['limitRate_bianSell_huobiBuy']=row[4]

    except Exception,e:
        #print "数据库中查询coins错误"
        logger.log("数据库中查询coins错误")
        logger.log(e)

    # 关闭数据库连接
    db.close()

    return coins


def insertBalanceTable(targetCoin,baseCoin,balance_targetCoin_bian,balance_baseCoin_bian,balance_targetCoin_huobi,balance_baseCoin_huobi):

    pwd=""
    if 'macbook' in socket.getfqdn(socket.gethostname()):pwd='root'
    else:pwd='Zhuwenin841002*'
    db = mysql.connector.connect(user='root', password=pwd, database='coin', use_unicode=True)
    cursor = db.cursor()
    # SQL 查询语句
    sql = "insert into balance_normal (miner,targetCoin,baseCoin,balance_targetCoin_bian,balance_baseCoin_bian,balance_targetCoin_huobi,balance_baseCoin_huobi) " \
          "values ('%s','%s','%s','%f','%f','%f','%f')" % ('kyoto',targetCoin,baseCoin,balance_targetCoin_bian,balance_baseCoin_bian,balance_targetCoin_huobi,balance_baseCoin_huobi)
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
        logger.log("insert balance_normal table finish")

    except:
        db.rollback()
        logger.log("insert balance_normal table error")

    # 关闭数据库连接
    db.close()


if __name__ == '__main__':

    insertRate('XRP','BTC','2018-01-25 12:23:19',-0.15,-0.16)