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

if __name__ == '__main__':

    print 'goto get all symbols'
    symbolsInHuobi=[]
    symbolsInBian=[]
    urlHuobi="https://api.huobi.pro/v1/common/symbols"
    urlBian="https://api.binance.com/api/v3/ticker/price"

    #bian
    try:
        request = urllib2.Request(urlBian)
        request.add_header('Content-Type', 'application/x-www-form-urlencoded')
        response = urllib2.urlopen(request,timeout = 15)
        data = json.load(response)
        for item in data:
            symbolsInBian.append(item['symbol'].lower())

    except Exception,e:

        print e
        print 'get symbols from bian error'

    #huobi
    try:
        targetCoin=""
        baseCoin=""
        symbol=""
        request = urllib2.Request(urlHuobi)
        request.add_header('Content-Type', 'application/x-www-form-urlencoded')
        request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36')
        response = urllib2.urlopen(request,timeout = 15)
        data = json.load(response)
        for item in data['data']:
            #print item
            targetCoin=item["base-currency"]
            baseCoin=item["quote-currency"]
            symbol = "%s%s" % (targetCoin,baseCoin)
            symbolsInHuobi.append(symbol)
        #print symbolsInHuobi


    except Exception,e:

        print e
        print 'query all symbols in huobi error'

    #比较两个列表，找出同时存在的 BCC BCH
    #print symbolsInHuobi
    #print symbolsInBian
    for symbol in symbolsInHuobi:

        try:
            if symbolsInBian.index(symbol):#find it

                print symbol
                #防止重复插入，下次补上
                dao.saveSymbol(symbol)

        except Exception:

            pass