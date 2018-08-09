import threading

num=0

def func1():

    global num

    num += 5
    num += 5

if __name__ == '__main__':


    threads = []
    t1= threading.Thread(target=func1)
    threads.append(t1)

    for t in threads:

        t.setDaemon(True)
        t.start()

    while (1):

        print num
