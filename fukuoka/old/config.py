#coding=utf-8

#账户部分的配置

#bian limits
# rateLimit:"REQUESTS","MINUTE","limit":1200
# rateLimitType:"ORDERS","SECOND","limit":10
# rateLimitType:"ORDERS","DAY","limit":100000
binanceRef={

    'tradeCost':0.001,#扣除收取到的资产
    'endpoint':'https://api.binance.com',
    'accountInfoUrl':'/api/v3/account',# GET HMAC SHA256
    'tradeUrl':'/api/v3/order', #POST (HMAC SHA256)
    'priceUrl':'/api/v1/depth',
    'secretKey':'kOVb4rpqjJHHjUskd6Ynbrjoq6hW1sH3lOOClYnfeJrNtrKzDzJcFNReVPoRoqTs',
    'apikey':'wxYD2BTEJicu1fMrSesVnQHKIGmB0r8jQkQghHAbWmRZTqZfBqWwIkZP86xVClV3',
    'websocket_endpoint':"wss://stream.binance.com:9443/ws/xrpbtc@depth5"

}

#huobi
#限制频率（每个接口，只针对交易api，行情api不限制）为10秒100次。
huobiRef={

    'endpoint':'https://api.huobi.pro',
    'account-id':'848426',
    'tradeCost':0.002,#扣除收取到的资产
    'accountInfoUrl':'/v1/account/accounts/',
    'tradeUrl':'/v1/order/orders/place',
    'host':'api.huobi.pro',
    'priceUrl':'https://api.huobi.pro/market/depth',
    'apikey':'48e18439-80d2ca0c-d52bbe60-13fd4',
    'secretkey':'e739e348-d70a9a75-ded9e4cc-232b7',
    'websocket_endpoint':"wss://api.huobipro.com/ws"


}

#公共配置
minTradeNum={

    'BCH/BTC':0.001,
    'XRP/BTC':1,
    'ETH/USDT':0.0001,
    'LTC/USDT':0.0001,

}
#minTradeNum=0.0001
#smskeyID='LTAI4QC86RgQgLNZ'
#smskeySecret='tWqDnoYGOXkGgD6jKFkmj6ZtPokrzf'




