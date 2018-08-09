import datetime
import time


def getAccurateOfNumber(number):

    numberStr = str(number)
    if '.' in numberStr:
        indexOfPoint = numberStr.index('.')
        accurate=len(numberStr)-indexOfPoint-1
        return accurate

    else:
        return 0


def getZeroOflength(length):

    str='0.'
    for i in range(0,length-1):

        str += '0'
    str += '1'
    number=float(str)
    return number

def getTime():

    time1=datetime.datetime.now()
    time.sleep(3)
    time2=datetime.datetime.now()
    return (time2-time1).total_seconds()


def getMin():

    return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))


print getMin()
