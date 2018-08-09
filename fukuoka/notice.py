#coding=utf-8
#!/usr/bin/python

import sys
import os
import socket
import hashlib
import urllib2
import xml.etree.ElementTree as ET
import json
import time
import myLogger
reload(sys)
sys.setdefaultencoding("utf-8")


def sendTextInfo(title,content1,content2,remark):

    try:
        #print 'sendTextInfo'
        post_data = {
                    "touser":'owmz2w6UGRbjLqEPGB8AWa2nK5rw',
                    "template_id":"TAwWy-Am9SnHUAfKVhMnzTIUWMFPQyvwuDNbZx0plM4",
                    "data":{
                        "first": {
                            "value":title,
                            "color":"#173177"
                        },
                        "keyword1":{
                            "value":content1,
                            "color":"#173177"
                        },
                        "keyword2": {
                            "value":content2,
                            "color":"#173177"
                        },
                        "remark":{
                            "value":remark,
                            "color":"#173177"
                        }
                    }
        }
        #print post_data

        #xml解析在服务器的2.6环境下有问题！
        workPath="/usr/local/bin/projects/fukuoka/"
        filePath=workPath+'properties.xml'
        tree = ET.ElementTree(file=filePath)
        root = tree.getroot()
        for child_of_root in root:

            #print child_of_root
            if child_of_root.tag == "access_token":

                accessToken=child_of_root.text
                #print accessToken

        requrl = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token="+accessToken
        headers = {'Content-Type': 'application/json'}
        request = urllib2.Request(url=requrl, headers=headers, data=json.dumps(post_data))
        response = urllib2.urlopen(request)
        jsonResult=json.load(response)
        #print jsonResult
        #return jsonResult['msgid']


    except Exception,e:

        print e
        myLogger.log("send notice error:")
        myLogger.log(e)

if __name__ == '__main__':

    sendTextInfo("test","test","test","test")