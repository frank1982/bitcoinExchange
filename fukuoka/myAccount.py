#coding=utf-8
#!/usr/bin/python

import requests
import myConfig
import datetime
import urllib
import base64
import hmac
import hashlib
import urllib2
import json
import myLogger
import time
import math

def order_bian(buyOrSell,targetCoin,baseCoin,quantity,price):

    symbol = targetCoin+baseCoin
    side = buyOrSell
    type = "LIMIT"
    quantity = quantity
    price = price
    timestamp = int(round(time.time() * 1000))


    requestBody = ""
    requestBody += "symbol="+targetCoin+baseCoin
    requestBody += "&side="+buyOrSell
    requestBody += "&type="+type
    requestBody += "&timeInForce=FOK" #GTC
    requestBody += "&quantity="+str(quantity)
    requestBody += "&price="+str(price)
    #requestBody += "&recvWindow=5000"
    requestBody += "&timestamp="+str(timestamp)
    #print requestBody

    #sha256
    signature = sha256(requestBody,myConfig.binanceRef['secretKey'])
    #print signature
    requestBody += "&signature="+signature
    #post

    try:

        headers = {

            'X-MBX-APIKEY': myConfig.binanceRef['apikey'],
            'Content-Type':'application/x-www-form-urlencoded'
        }

        url = myConfig.binanceRef['endpoint']+myConfig.binanceRef['tradeUrl']+'?'+requestBody
        myLogger.log(url)
        r = requests.post(url,headers=headers)
        myLogger.log(r.json())
        if r.status_code == 200:

            result = r.json()	
            status = result['status']
            if status == "FILLED":#完全成交
                return "SUCCESS"
            else:
                myLogger.log("trade failed in bian")
                myLogger.log(r.json())
                return "FAILED"

        else:
            myLogger.log("networkError in bian")
            myLogger.log(r.json())
            return "networkError"
        #status":"FILLED
        #返回的结果 status 有 NEW FILLED

    except Exception,e:

        print '币安交易失败'
        print e
        return "networkError"
        myLogger.log('币安交易失败')
        myLogger.log(e)


def order_bian_GTC(buyOrSell,targetCoin,baseCoin,quantity,price):

    orderResult={}
    symbol = targetCoin+baseCoin
    side = buyOrSell
    type = "LIMIT"
    quantity = quantity
    price = price
    timestamp = int(round(time.time() * 1000))


    requestBody = ""
    requestBody += "symbol="+targetCoin+baseCoin
    requestBody += "&side="+buyOrSell
    requestBody += "&type="+type
    requestBody += "&timeInForce=GTC" #GTC
    requestBody += "&quantity="+str(quantity)
    requestBody += "&price="+str(price)
    #requestBody += "&recvWindow=5000"
    requestBody += "&timestamp="+str(timestamp)
    #print requestBody

    #sha256
    signature = sha256(requestBody,myConfig.binanceRef['secretKey'])
    #print signature
    requestBody += "&signature="+signature
    #post

    try:

        headers = {

            'X-MBX-APIKEY': myConfig.binanceRef['apikey'],
            'Content-Type':'application/x-www-form-urlencoded'
        }

        url = myConfig.binanceRef['endpoint']+myConfig.binanceRef['tradeUrl']+'?'+requestBody
        myLogger.log(url)
        r = requests.post(url,headers=headers)
        print r.json()
        if r.status_code == 200:

            orderResult = r.json()
            myLogger.log(orderResult)
            return orderResult

        else:
            myLogger.log("trade error in bian")
            myLogger.log(r.json())
            return orderResult


    except Exception,e:

        myLogger.log('币安交易失败')
        myLogger.log(e)
        return orderResult



def submitcancel_huobi(orderIdStr):

    #POST /v1/order/orders/{order-id}/submitcancel
    cancelResult={}
    params = {
              "order-id": orderIdStr,

             }

    timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
    params_to_sign = {
                      'AccessKeyId': myConfig.huobiRef['apikey'],
                      'SignatureMethod': 'HmacSHA256',
                      'SignatureVersion': '2',
                      'Timestamp': timestamp
                     }

    host_url = myConfig.huobiRef['endpoint']
    host_name = myConfig.huobiRef['host']
    submitcancekUrl="/v1/order/orders/"+params["order-id"]+"/submitcancel"
    params_to_sign['Signature'] = createSign(params_to_sign,'POST', host_name, submitcancekUrl, myConfig.huobiRef['secretkey'])
    url = host_url + submitcancekUrl + '?' + urllib.urlencode(params_to_sign)

    headers = {
        "Accept": "application/json",
        'Content-Type': 'application/json',
        "User-Agent": "Chrome/39.0.2171.71",
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0'
    }
    postdata = json.dumps(params)

    try:
        response = requests.post(url, postdata, headers=headers, timeout=15)


        if response.status_code == 200:


            cancelResult = response.json()
            myLogger.log(cancelResult)
            return cancelResult

        else:

            return response.json()

    except Exception as e:

        myLogger.log("httpPost failed, detail is:%s" % e)
        return cancelResult




#GET /v1/order/orders/{order-id} 查询某个订单详情 huobi
def getTradeDetail_huobi(orderIdStr):

    tradeResult={}
    messageStr=""
    messageStr += "GET\n"
    messageStr += "api.huobi.pro\n"
    messageStr += "/v1/order/orders/"
    messageStr += orderIdStr+"\n"
    messageStr += "AccessKeyId="+myConfig.huobiRef['apikey']
    messageStr += "&SignatureMethod=HmacSHA256&SignatureVersion=2"
    timeStr=datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
    timeStrEncodeUrl=urllib.quote(timeStr.encode('utf-8', 'replace'))
    messageStr += "&Timestamp="+timeStrEncodeUrl

    base64Str = base64Func(messageStr,myConfig.huobiRef['secretkey'])
    base64StrEncodeUrl=urllib.quote(base64Str.encode('utf-8', 'replace'))


    urlStr=""
    urlStr += myConfig.huobiRef['endpoint']+"/v1/order/orders/"+orderIdStr+"?"
    urlStr += "AccessKeyId="+myConfig.huobiRef['apikey']
    urlStr += "&SignatureMethod=HmacSHA256&SignatureVersion=2&Timestamp="+timeStrEncodeUrl
    urlStr += "&Signature="+base64StrEncodeUrl

    request = urllib2.Request(urlStr)
    request.add_header('Content-Type', 'application/x-www-form-urlencoded')
    request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36')

    try:
        response = urllib2.urlopen(request,timeout = 15)
        tradeResult = json.load(response)
        myLogger.log(tradeResult)
        return tradeResult


    except Exception,e:

        myLogger.log("get trade detail of huobi error")
        return tradeResult




#限价单
def order_huobi(buyOrSell,targetCoin,baseCoin,quantity,price):#limit 限价单

    orderResult={}
    params = {
              "account-id": myConfig.huobiRef['account-id'],
              "amount": quantity,
              "symbol": targetCoin+baseCoin,
              "type": buyOrSell.lower()+"-limit",
              "source": "api",
              "price":price,
             }

    timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
    params_to_sign = {
                      'AccessKeyId': myConfig.huobiRef['apikey'],
                      'SignatureMethod': 'HmacSHA256',
                      'SignatureVersion': '2',
                      'Timestamp': timestamp
                     }

    host_url = myConfig.huobiRef['endpoint']
    host_name = myConfig.huobiRef['host']
    params_to_sign['Signature'] = createSign(params_to_sign,'POST', host_name, myConfig.huobiRef['tradeUrl'], myConfig.huobiRef['secretkey'])
    url = host_url + myConfig.huobiRef['tradeUrl'] + '?' + urllib.urlencode(params_to_sign)
    myLogger.log(url)
    headers = {
        "Accept": "application/json",
        'Content-Type': 'application/json',
        "User-Agent": "Chrome/39.0.2171.71",
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0'
    }
    postdata = json.dumps(params)

    try:
        response = requests.post(url, postdata, headers=headers, timeout=15)

        if response.status_code == 200:

            #status error "ok"
            orderResult = response.json()
            myLogger.log(orderResult)
            return orderResult


        else:
            myLogger.log("trade error in huobi")
            myLogger.log(response.json())
            return orderResult

    except Exception as e:

        myLogger.log("trade error in huobi")
        myLogger.log(e)
        return orderResult



#immediate or cancel
def order_huobi_IOC(buyOrSell,targetCoin,baseCoin,quantity,price):#limit 限价单

    orderResult={}
    params = {
              "account-id": myConfig.huobiRef['account-id'],
              "amount": quantity,
              "symbol": targetCoin+baseCoin,
              "type": buyOrSell.lower()+"-ioc",
              "source": "api",
              "price":price,
             }
    print params
    timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
    params_to_sign = {
                      'AccessKeyId': myConfig.huobiRef['apikey'],
                      'SignatureMethod': 'HmacSHA256',
                      'SignatureVersion': '2',
                      'Timestamp': timestamp
                     }

    host_url = myConfig.huobiRef['endpoint']
    host_name = myConfig.huobiRef['host']
    params_to_sign['Signature'] = createSign(params_to_sign,'POST', host_name, myConfig.huobiRef['tradeUrl'], myConfig.huobiRef['secretkey'])
    url = host_url + myConfig.huobiRef['tradeUrl'] + '?' + urllib.urlencode(params_to_sign)
    myLogger.log(url)
    headers = {
        "Accept": "application/json",
        'Content-Type': 'application/json',
        "User-Agent": "Chrome/39.0.2171.71",
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0'
    }
    postdata = json.dumps(params)

    try:
        response = requests.post(url, postdata, headers=headers, timeout=15)

        if response.status_code == 200:

            #status error "ok"
            orderResult = response.json()
            myLogger.log(orderResult)
            print orderResult
            return orderResult


        else:
            myLogger.log("trade error in huobi")
            myLogger.log(response.json())
            return orderResult

    except Exception as e:

        myLogger.log("trade error in huobi")
        myLogger.log(e)
        return orderResult


def base64Func(messageStr,secretStr):#huobi base64加密

    message = bytes(messageStr).encode('utf-8')
    secret = bytes(secretStr).encode('utf-8')
    return base64.b64encode(hmac.new(secret, message, digestmod=hashlib.sha256).digest())


def queryBalance_huobi(targetCoin,baseCoin):#Coin用大写

    myLogger.log("queryBalance_huobi")
    lowTargetCoin=targetCoin.lower()
    lowBaseCoin=baseCoin.lower()
    messageStr=""
    messageStr += "GET\n"
    messageStr += "api.huobi.pro\n"
    messageStr += myConfig.huobiRef['accountInfoUrl']
    messageStr += myConfig.huobiRef['account-id']+"/balance\n"
    messageStr += "AccessKeyId="+myConfig.huobiRef['apikey']
    messageStr += "&SignatureMethod=HmacSHA256&SignatureVersion=2"
    timeStr=datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
    timeStrEncodeUrl=urllib.quote(timeStr.encode('utf-8', 'replace'))
    messageStr += "&Timestamp="+timeStrEncodeUrl

    base64Str = base64Func(messageStr,myConfig.huobiRef['secretkey'])
    base64StrEncodeUrl=urllib.quote(base64Str.encode('utf-8', 'replace'))


    urlStr=""
    urlStr += myConfig.huobiRef['endpoint']+myConfig.huobiRef['accountInfoUrl']+myConfig.huobiRef['account-id']+"/balance?"
    urlStr += "AccessKeyId="+myConfig.huobiRef['apikey']
    urlStr += "&SignatureMethod=HmacSHA256&SignatureVersion=2&Timestamp="+timeStrEncodeUrl
    urlStr += "&Signature="+base64StrEncodeUrl

    request = urllib2.Request(urlStr)
    request.add_header('Content-Type', 'application/x-www-form-urlencoded')
    request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36')
    response = urllib2.urlopen(request,timeout = 15)
    data = json.load(response)
 

    try:

        balance_huobi={}
        for index, item in enumerate(data['data']['list']):

            #print item
            tmpItem={}

            if item['currency'] == lowTargetCoin and item['type'] == 'trade':

                balance_huobi[targetCoin] = float(item['balance'])

            elif item['currency'] == lowBaseCoin and item['type'] == 'trade':

                balance_huobi[baseCoin] = float(item['balance'])

        myLogger.log("balance_huobi:")
        myLogger.log(balance_huobi)
        return balance_huobi

    except Exception,e:

        #print '查询火币账户余额失败'
        print e
        myLogger.log('enquire huobi balance error')
        myLogger.log(e)
        #print e

def queryBalance_bian(targetCoin,baseCoin):

    myLogger.log("queryBalance_bian")
    balance_bian={}
    timestamp = int(round(time.time() * 1000))
    #print timestamp
    queryString = "recvWindow=5000&timestamp="+str(timestamp)
    #print queryString
    signature = sha256(queryString,myConfig.binanceRef['secretKey'])
    #print signature

    fullurl = ""
    fullurl += myConfig.binanceRef['endpoint']
    fullurl += myConfig.binanceRef['accountInfoUrl']+"?"
    fullurl += queryString+"&"
    fullurl += "signature="+signature
    try:

        request = urllib2.Request(fullurl)
        request.add_header('X-MBX-APIKEY', myConfig.binanceRef['apikey'])
        response = urllib2.urlopen(request,timeout = 15)
        data = json.load(response)

        for index, item in enumerate(data['balances']):

            tmpItem={}
            if item['asset'] == targetCoin:

                balance_bian[targetCoin] = float(item['free'].encode('utf-8'))

            elif item['asset'] == baseCoin:

                balance_bian[baseCoin] = float(item['free'].encode('utf-8'))

        myLogger.log("balance_bian:")
        myLogger.log(balance_bian)
        return balance_bian

    except Exception,e:
        print e


def getTradeDetail_bian(symbol,orderId):#symbol:"LTCBTC" orderId:1 #long

    tradeDetailResult={}
    timestamp = int(round(time.time() * 1000))
    #print timestamp
    queryString = "symbol="+symbol+"&"
    queryString += "orderId="+str(orderId)+"&"
    queryString += "recvWindow=5000&timestamp="+str(timestamp)
    #print queryString
    signature = sha256(queryString,myConfig.binanceRef['secretKey'])
    #print signature

    fullurl = ""
    fullurl += myConfig.binanceRef['endpoint']
    fullurl += "/api/v3/order?"
    fullurl += queryString+"&"
    fullurl += "signature="+signature

    try:

        request = urllib2.Request(fullurl)
        request.add_header('X-MBX-APIKEY', myConfig.binanceRef['apikey'])
        response = urllib2.urlopen(request,timeout = 15)
        tradeDetailResult = json.load(response)
        myLogger.log(tradeDetailResult)
        return tradeDetailResult

    except Exception,e:
        myLogger.log("get trade detail of bian wrong")
        myLogger.log(e)
        return tradeDetailResult


def sha256(messageStr,secretStr):#hmac sha256加密

   signature = hmac.new(secretStr, messageStr, digestmod=hashlib.sha256).digest()
   return toHex(signature)

def toHex(str):#转16进制
    lst = []
    for ch in str:
        hv = hex(ord(ch)).replace('0x', '')
        if len(hv) == 1:
            hv = '0' + hv
        lst.append(hv)
    return reduce(lambda x, y: x + y, lst);



def createSign(pParams, method, host_url, request_path, secret_key):

    sorted_params = sorted(pParams.items(), key=lambda d: d[0], reverse=False)
    encode_params = urllib.urlencode(sorted_params)
    payload = [method, host_url, request_path, encode_params]
    payload = '\n'.join(payload)
    payload = payload.encode(encoding='UTF8')
    secret_key = secret_key.encode(encoding='UTF8')
    digest = hmac.new(secret_key, payload, digestmod=hashlib.sha256).digest()
    signature = base64.b64encode(digest)
    signature = signature.decode()
    return signature


def order_bian_market(buyOrSell,targetCoin,baseCoin,quantity):

    print('start order_bian_market')
    symbol = targetCoin+baseCoin
    side = buyOrSell
    type = "MARKET"
    quantity = quantity
    timestamp = int(round(time.time() * 1000))

    requestBody = ""
    requestBody += "symbol="+targetCoin+baseCoin
    requestBody += "&side="+buyOrSell
    requestBody += "&type="+type
    requestBody += "&quantity="+str(quantity)
    requestBody += "&timestamp="+str(timestamp)

    signature = sha256(requestBody,myConfig.binanceRef['secretKey'])
    requestBody += "&signature="+signature

    try:

        headers = {

            'X-MBX-APIKEY': myConfig.binanceRef['apikey'],
            'Content-Type':'application/x-www-form-urlencoded'
        }

        url = myConfig.binanceRef['endpoint']+myConfig.binanceRef['tradeUrl']+'?'+requestBody
        r = requests.post(url,headers=headers)
        print('bian trade result: %s' % r.json())
        print(r.json())

        if r.status_code == 200:

            result = r.json()
            status = result['status']

            if status == "FILLED":#完全成交
                return "SUCCESS"
            else:
                return "FAILED"

        else:

            print("statusError")
            return "statusError"


        #status":"FILLED
        #返回的结果 status 有 NEW FILLED
    except Exception,e:
        print e
        print('bian trade error')
        return "networkError"


if __name__ == '__main__':

    #print queryBalance_huobi('STEEM',"ETH") #Coin用大写
    #print queryBalance_bian('STEEM',"ETH")
    #changeAccurateOfNumber(0.000701211)
    #order_huobi_IOC("SELL",'steem',"eth",2,0.003411)#火币用小写输入
    #order_bian("BUY",'STEEM',"USDT",5,0.003588)
    print order_bian_market("SELL",'ETH',"USDT",1.633)
    #print getTradeDetail_huobi('5672797941')
    #submitcancel_huobi("5278340230")
    #getTradeDetail_bian("STEEMETH",7574719)
    pass
    # huobi sell 挂单
    #{u'status': u'ok', u'data': u'5672797941'}
    '''
    {u'status': u'ok', u'data':
    {u'account-id': 848426, u'canceled-at': 0, u'finished-at': 0,
     u'field-cash-amount': u'0.0', u'price': u'0.003910000000000000',
     u'created-at': 1528726981999, u'state': u'submitted',
     u'id': 5672797941, u'field-amount': u'0.0', u'amount': u'2.000000000000000000',
      u'source': u'api', u'field-fees': u'0.0', u'type': u'sell-limit', u'symbol': u'steemeth'}
    }
    '''

