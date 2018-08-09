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

#策略更换为异步等待每次交易结果
#定义全局变量
_tradeData=[]#存储交易记录
