import asyncio
import sys
import threading
import time
from urllib.request import urlopen


# to use
# t1 = InternetMonitor(1, network_connection) //create class InternetMonitor(input_delay_sec,  var_status)
# object will destroy if internet work


def checkNet(network):
    try:
        for timeout in [1, 5, 10, 15]:
            response = urlopen('http://google.com', timeout=timeout)
        if network["status"]:
            network["status"] = True
            network["isChange"] = False
        else:
            network["status"] = True
            network["isChange"] = True
    except:
        if network["status"]:
            network["status"] = False
            network["isChange"] = True
        else:
            network["status"] = False
            network["isChange"] = False


class InternetMonitor(threading.Thread):
    def __init__(self, interval_secs, network, func_ticker):
        threading.Thread.__init__(self)
        self.internet = network
        self.network_fail = True
        self.interval_secs = interval_secs
        self.checkingServer = 'http://google.com'
        self.start()

    def is_internet_on(self):
        for timeout in [1, 5, 10, 15]:
            try:
                response = urlopen(self.checkingServer, timeout=timeout)
                return True
            except:
                return False
        return False

    def run(self):
        while self.network_fail:
            time.sleep(self.interval_secs)
            try:
                self.internet["status"] = self.is_internet_on()
                self.internet["isChange"] = True
                self.network_fail = False
            except:
                print("Inet \t ----------- Error -------------")
                continue
        # print("Done")
