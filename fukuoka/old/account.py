#coding=utf-8
#!/usr/bin/python


import config
import datetime
import urllib
import base64
import hmac
import hashlib
import urllib2
import json
import logger
import time
import requests


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


#市价单
def order_huobi_market(buyOrSell,targetCoin,baseCoin,quantity):
    #quantity 限价单表示下单数量，市价买单时表示买多少钱，市价卖单时表示卖多少币

    params = {
              "account-id": config.huobiRef['account-id'],
              "amount": quantity,
              "symbol": targetCoin+baseCoin,
              "type": buyOrSell.lower()+"-market",
              "source": "api",
              }

    timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
    params_to_sign = {
                      'AccessKeyId': config.huobiRef['apikey'],
                      'SignatureMethod': 'HmacSHA256',
                      'SignatureVersion': '2',
                      'Timestamp': timestamp
                     }

    host_url = config.huobiRef['endpoint']
    host_name = config.huobiRef['host']
    params_to_sign['Signature'] = createSign(params_to_sign,'POST', host_name, config.huobiRef['tradeUrl'], config.huobiRef['secretkey'])
    url = host_url + config.huobiRef['tradeUrl'] + '?' + urllib.urlencode(params_to_sign)

    headers = {
        "Accept": "application/json",
        'Content-Type': 'application/json',
        "User-Agent": "Chrome/39.0.2171.71",
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0'
    }
    postdata = json.dumps(params)

    try:
        #response = requests.post(url, postdata, headers=headers, timeout=15)
        response = requests.post(url, postdata, headers=headers)
        logger.log("'huobi trade result: %s" % response.json())

        if response.status_code == 200:

            #status error "ok"
            result = response.json()
            status = result['status']

            if status == "ok":#交易成功

                return "SUCCESS"
            else:

                return "FAILED"

            #{u'status': u'ok', u'data': u'470064933'}

        else:

            logger.log("huobi trade networkError: %s" % response.json())
            #logger.log(response.json())
            return "networkError"


    except Exception as e:

        logger.log("httpPost failed, detail is:%s" % e)
        return "networkError"


def order_bian_market(buyOrSell,targetCoin,baseCoin,quantity):

    logger.log('start order_bian_market')
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

    signature = sha256(requestBody,config.binanceRef['secretKey'])
    requestBody += "&signature="+signature

    try:

        headers = {

            'X-MBX-APIKEY': config.binanceRef['apikey'],
            'Content-Type':'application/x-www-form-urlencoded'
        }

        url = config.binanceRef['endpoint']+config.binanceRef['tradeUrl']+'?'+requestBody
        r = requests.post(url,headers=headers)
        logger.log('bian trade result: %s' % r.json())
        #logger.log(r.json())

        if r.status_code == 200:

            result = r.json()
            status = result['status']

            if status == "FILLED":#完全成交
                return "SUCCESS"
            else:
                return "FAILED"

        else:

            logger.log("statusError")
            return "statusError"


        #status":"FILLED
        #返回的结果 status 有 NEW FILLED
    except Exception,e:
        print e
        logger.log('bian trade error')
        logger.log(e)
        return "networkError"




def base64Func(messageStr,secretStr):#huobi base64加密

    message = bytes(messageStr).encode('utf-8')
    secret = bytes(secretStr).encode('utf-8')
    return base64.b64encode(hmac.new(secret, message, digestmod=hashlib.sha256).digest())


def queryBalance_huobi(targetCoin,baseCoin):

    lowTargetCoin=targetCoin.lower()
    lowBaseCoin=baseCoin.lower()
    messageStr=""
    messageStr += "GET\n"
    messageStr += "api.huobi.pro\n"
    messageStr += config.huobiRef['accountInfoUrl']
    messageStr += config.huobiRef['account-id']+"/balance\n"
    messageStr += "AccessKeyId="+config.huobiRef['apikey']
    messageStr += "&SignatureMethod=HmacSHA256&SignatureVersion=2"
    timeStr=datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
    timeStrEncodeUrl=urllib.quote(timeStr.encode('utf-8', 'replace'))
    messageStr += "&Timestamp="+timeStrEncodeUrl

    base64Str = base64Func(messageStr,config.huobiRef['secretkey'])
    base64StrEncodeUrl=urllib.quote(base64Str.encode('utf-8', 'replace'))


    urlStr=""
    urlStr += config.huobiRef['endpoint']+config.huobiRef['accountInfoUrl']+config.huobiRef['account-id']+"/balance?"
    urlStr += "AccessKeyId="+config.huobiRef['apikey']
    urlStr += "&SignatureMethod=HmacSHA256&SignatureVersion=2&Timestamp="+timeStrEncodeUrl
    urlStr += "&Signature="+base64StrEncodeUrl

    request = urllib2.Request(urlStr)
    request.add_header('Content-Type', 'application/x-www-form-urlencoded')
    response = urllib2.urlopen(request,timeout = 15)
    data = json.load(response)

    try:

        balance_huobi={}
        for index, item in enumerate(data['data']['list']):

            #print item
            tmpItem={}

            if item['currency'] == lowTargetCoin and item['type'] == 'trade':

                balance_huobi[targetCoin] = float(item['balance'].encode('utf-8'))

            elif item['currency'] == lowBaseCoin and item['type'] == 'trade':

                balance_huobi[baseCoin] = float(item['balance'].encode('utf-8'))

        return balance_huobi

    except Exception,e:

        #print '查询火币账户余额失败'
        print e
        logger.log('enquire huobi balance error')
        logger.log(e)
        #print e

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


def queryBalance_bian(targetCoin,baseCoin):


    balance_bian={}
    timestamp = int(round(time.time() * 1000))
    #print timestamp
    queryString = "recvWindow=5000&timestamp="+str(timestamp)
    #print queryString
    signature = sha256(queryString,config.binanceRef['secretKey'])
    #print signature

    fullurl = ""
    fullurl += config.binanceRef['endpoint']
    fullurl += config.binanceRef['accountInfoUrl']+"?"
    fullurl += queryString+"&"
    fullurl += "signature="+signature
    print fullurl
    try:

        request = urllib2.Request(fullurl)
        request.add_header('X-MBX-APIKEY', config.binanceRef['apikey'])
        response = urllib2.urlopen(request,timeout = 15)
        data = json.load(response)
        print "balance:"+data['balances']#各种货币的数组
        for index, item in enumerate(data['balances']):

            tmpItem={}
            if item['asset'] == targetCoin:

                balance_bian[targetCoin] = float(item['free'].encode('utf-8'))

            elif item['asset'] == baseCoin:

                balance_bian[baseCoin] = float(item['free'].encode('utf-8'))

        return balance_bian

    except Exception,e:
        print e
        logger.log('enquire bian balance error')
        logger.log(e)

if __name__ == '__main__':
    #huobi
    #访问
    #48e18439-80d2ca0c-d52bbe60-13fd4
    #私密
    #e739e348-d70a9a75-ded9e4cc-232b7
    pass
    #print order_bian_market("SELL",'XRP','BTC',3)
    print order_huobi_market("SELL",'xrp','btc',0.000300)
    #print queryBalance_huobi('XRP','BTC')
    #print queryBalance_bian('ETH','USDT')

