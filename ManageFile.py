import os 
from datetime import datetime

def getFilePath():
    last_name = os.listdir("Pictures")[-1][-8:-4]
    n = int(last_name)+1
    num = str(n)
    while len(num)<4:
        num = '0'+num
    return ("Pictures/"+datetime.today().strftime('%Y%m%d')+"_%s.jpg" % num)