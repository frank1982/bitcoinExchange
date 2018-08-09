#coding=utf-8
#!/usr/bin/python
import os
import logging


rootPath = __file__[:-12]
#print rootPath
logPath = rootPath+"/myapp.log"
logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                filename=logPath,
                filemode='a')

#logging.debug('This is debug message')
#logging.info('This is info message')
#logging.warning('This is warning message')
def log(msg):

    logging.info(msg)



