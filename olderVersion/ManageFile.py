import os
from datetime import datetime


def getFilePath_default():
    try:
        last_name = os.listdir("Pictures")[-1][-8:-4]
    except:
        os.mkdir("Pictures")
        erNum = '0'
        while len(erNum) < 4:
            erNum = '0'+erNum
        fz = open("initial_file_%s.jpg" % erNum, 'w')
        fz.close()
        last_name = os.listdir("Pictures")[-1][-8:-4]
    finally:
        num = str(last_name)
        while len(num) < 4:
            num = '0'+num
        return ("Pictures/"+datetime.today().strftime('%Y%m%d')+"_%s.jpg" % num)


def getFilePath():
    if not os.path.isdir('./Pictures'):
        os.mkdir("Pictures")
    return "Pictures/"+datetime.today().strftime('%Y%m%d')
