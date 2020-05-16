from PIL import Image
from Error_checker import passportScan
from picamera import PiCamera
from time import sleep
import re
import time
import pytesseract
from datetime import datetime

def scanMrzWithPi(pathImg = "Pictures/"+datetime.today().strftime('%Y%m%d')+".jpg", timeout = 180):
    camera = PiCamera()
    camera.resolution = (1024, 768)
    camera.start_preview()
    timein = datetime.now()
    while True: 
        try:
            camera.capture(pathImg)
            img = Image.open(pathImg)
            f = pytesseract.image_to_string(img)
            code=""
            for d in f.splitlines():
                #line of Machine Readable Zone
                print("Data:", d)
                if '<' in d:
                    #remove space for error scan
                    code+=re.sub(' ', '', d)[:44]
                    code+='\n'
            #print("ourcode :", code)
            if ((datetime.now()-timein).total_seconds() >= timeout):
                print((datetime.now()-timein).total_seconds())
                break
            p1 = passportScan(code)
            
            #if scan pass
            p1.printResult()
            print('\n')
            #print(p1.__dict__)
            break

        #else scan failed jump to except error and try again
        except ValueError as err:
            print(err)
            print ("------------------------------------------retry-----------------------------------------")
            continue
        except InterruptExecution:
            break
    #out of while loop
    camera.stop_preview()
    camera.close() 
    print("finish!")

class InterruptExecution (Exception):
    pass
