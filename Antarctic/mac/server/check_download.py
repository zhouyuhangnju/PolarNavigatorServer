import time
import argparse
import numpy as np
from getemail import checkemail
from getBounding import getCornerLonLats
import modisdownload.Get_Modis

import threading
import Queue

mutex = threading.Lock()

def print_ts(message):
    print("[%s] %s"%(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), message))

class check_mail(threading.Thread):
    def __init__(self, interval, command):
        threading.Thread.__init__(self)
        self.interval = interval
        self.command = command

    def run(self):
        self.check_mail(self.interval, self.command)

    def check_mail(self, interval, command):
        print_ts("-"*100)
        print_ts("Command %s"%command)
        print_ts("Starting every %s seconds."%interval)
        print_ts("-"*100)
        # start = True
        while True:
            try:
                # sleep for the remaining seconds of interval
                time_remaining = interval-time.time()%interval
                print_ts("Sleeping until %s (%s seconds)..."%((time.ctime(time.time()+time_remaining)), time_remaining))
                time.sleep(time_remaining)
                print_ts("Starting command.")

                # if start == True:
                #     # status = os.system(command)
                #     prenum = 0
                #     start = False

                prenum, subj = checkemail(args.email,args.password,args.pop3_server,0)
                # import random
                # if random.uniform(0, 1) > 0.5:
                #     subj = None
                # else:
                #     subj = '[south]165.0 127.0 65.0 45.0'
                # print '*** ' + str(subj)
                if subj != None:
                    value = subj[7:]
                    print(value)

                    # write file
                    range_file = open('range.txt', 'w')
                    range_file.write(value)
                    range_file.close()

                    global queue
                    if mutex.acquire(1):
                        print 'in check, queue is full is ' + str(queue.full())
                        if queue.full():
                            queue.get()
                        queue.put(value)
                        mutex.release()

                print_ts("-"*100)
                # print_ts("Command status = %s."%status)

            except Exception as e:
                print(e)

class download_hdf(threading.Thread):
    def __init__(self, interval):
        threading.Thread.__init__(self)
        self.interval = interval

    def run(self):
        self.download(self.interval)

    def download(self, interval):
        while True:
            try:
                global queue
                if mutex.acquire(1):
                    print 'in download, queue is full ' + str(queue.full())
                    if queue.full():
                        value = queue.get()
                        mutex.release()

                        print 'from queue get ' + value
                        values = value.split(' ')
                        # print values
                        EastBoundingCoord = float(values[1])
                        WestBoundingCoord = float(values[0])
                        SouthBoundingCoord = float(values[3])
                        NorthBoundingCoord = float(values[2])

                        #lonlist, latlist = getCornerLonLats(leftlon, leftlat, rightlon, rightlat)
                        #SouthBoundingCoord = np.min(latlist)
                        #NorthBoundingCoord = np.max(latlist)

                        # for i in range(len(lonlist)):
                        #    if lonlist[i] < 0:
                        #        lonlist[i] = lonlist[i] + 360

                        #maxCoord = np.max(lonlist)
                        # minCoord = np.min(lonlist)

                        #if maxCoord > 180:
                        #    maxCoord = maxCoord - 360
                        #if minCoord > 180:
                        #    minCoord = minCoord - 360

                        #if maxCoord*minCoord < 0 and abs(maxCoord-minCoord) < 180:
                        #    EastBoundingCoord = minCoord
                        #   WestBoundingCoord = maxCoord
                        # else:
                        #    EastBoundingCoord = maxCoord
                        #    WestBoundingCoord = minCoord

                        # print '******************************'
                        # print 'NorthBoundingCoord: ' + str(NorthBoundingCoord)
                        # print 'SouthBoundingCoord: ' + str(SouthBoundingCoord)
                        # print 'EastBoundingCoord: ' + str(EastBoundingCoord)
                        # print 'WestBoundingCoord: ' + str(WestBoundingCoord)
                        # print '******************************'

                        done = modisdownload.Get_Modis.maindownloading(EastBoundingCoord, WestBoundingCoord, SouthBoundingCoord, NorthBoundingCoord)
                        # import random
                        # if random.uniform(0, 2) > 1:
                        #     done = True
                        # else:
                        #     done = False
                        print '*** done is ' + str(done)
                        if not done:
                            if mutex.acquire(1):
                                print 'not done and queue is full is ' + str(queue.full())
                                if not queue.full():
                                    queue.put(value)
                                mutex.release()
                    else:
                        mutex.release()
                # sleep for the remaining seconds of interval
                time_remaining = interval-time.time()%interval
                time.sleep(time_remaining)
            except Exception as e:
                print(e)


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--email', help = 'email', type = str, default = 'PolarReceiveReq@lamda.nju.edu.cn')
    parser.add_argument('--password', help = 'password', type = str, default = 'PolarEmail1234')
    parser.add_argument('--pop3_server', help = 'pop3_server', type = str, default = '210.28.132.67')
    # parser.add_argument('--specified_email', help = 'specified_email', type = str, default = 'PolarSendReq@lamda.nju.edu.cn')
    args = parser.parse_args()
    interval_check = 600
    interval_down = 780
    queue = Queue.Queue(1)

    emailcheck = check_mail(interval_check, parser)
    hdfdownload = download_hdf(interval_down)
    emailcheck.start()
    # time.sleep(interval_check)
    hdfdownload.start()

