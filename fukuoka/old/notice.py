#coding=utf-8
#!/usr/bin/python

import sys
import os
import socket
import hashlib
import logger
import urllib2
import xml.etree.ElementTree as ET
import json
import time
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
        filePath='/home/ftper/projects/sakula/properties.xml'
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
        #return jsonResult['msgid']


    except Exception,e:

        logger.log("send wx info error")
        logger.log(e)


