#!/usr/bin/python
# coding=utf-8

import urllib2
import urllib
import json
import sys
import threading
import time

import xml.etree.ElementTree as ET




SETTINGS={

    'WEIXIN_ID':'gh_250953953f8a', #公众号微信ID
    'APPID':'wx0e2dc591178fa325',
    'SECRET':'3820685afb55088c32a565a0fb2f64c3',

}



#获取access_token
#http请求方式: GET
#https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=APPID&secret=APPSECRET
def getAccessToken():#每2个小时执行一次

    ACCESS_TOKEN_URL="https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s" %(SETTINGS['APPID'],SETTINGS['SECRET'])
    req = urllib2.Request(ACCESS_TOKEN_URL)

    def task():
        workPath="/usr/local/bin/projects/fukuoka/"
        print workPath
        res_data = urllib2.urlopen(req)
        print res_data
        res_data2 = res_data.read().decode("utf-8-sig")
        res = json.loads(res_data2)
        print res
        access_token=res['access_token']
        print access_token
        tree = ET.parse(workPath+'properties.xml')#要绝对目录
        root = tree.getroot()
        access_tokenNode=root.find('access_token')
        access_tokenNode.text=access_token
        tree.write(workPath+'properties.xml')#要绝对目录

    #首次启动先执行一次，2小时执行一次

    while True:

        task()
        time.sleep(7200)



if __name__ == '__main__':



    threads = []
    #以子线程方式启动定时获取access_token的任务。2小时一次
    t1 = threading.Thread(target=getAccessToken)
    threads.append(t1)


    for t in threads:

        #t.setDaemon(True)
        t.start()
    for t in threads:

        #t.setDaemon(True)
        t.join()


