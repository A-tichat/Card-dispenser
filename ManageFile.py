import os
from datetime import datetime


def getFilePath():
    try:
        last_name = os.listdir("Pictures")[-1][-8:-4]
    except:
        os.mkdir("Pictures")
        erNum = '0'
        while len(erNum) < 4:
            erNum = '0'+erNum
        fz = open("Pictures/"+datetime.today().strftime('%Y%m%d') +
                  "_%s.jpg" % erNum, 'w')
        fz.close()
        last_name = os.listdir("Pictures")[-1][-8:-4]
    n = int(last_name)+1
    num = str(n)
    while len(num) < 4:
        num = '0'+num
    return ("Pictures/"+datetime.today().strftime('%Y%m%d')+"_%s.jpg" % num)
