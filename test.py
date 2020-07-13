import threading
import time
import logging
import socket


def connect(host="8.8.8.8", port=53, timeout=3):
    try:
        global stat
        global stop_thread
        time.sleep(3)
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        print("true")
        if(stat < 1):
            print("+++", stat)
            stat = 2
        if not stop_thread:
            connect()
    except socket.error as ex:
        print(ex)
        print("false")
        if (stat > 1):
            print("---", stat)
            stat = 0
        if not stop_thread:
            connect()


if __name__ == "__main__":
    try:
        stat = 0
        stop_thread = False
        checkNetwork = threading.Thread(target=connect)
        checkNetwork.start()
        while 1:
            print('m')
            time.sleep(1)
    finally:
        stop_thread = True
