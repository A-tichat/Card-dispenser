import asyncio, logging, os
import random, time, threading, re
import urllib.request
import pytesseract
from picamera import PiCamera
from PIL import Image
from nextion import Nextion, EventType
from smbus2 import SMBus, i2c_msg
from mysql.connector import Error
from datetime import datetime

import key_mysql 
from ManageFile import getFilePath
from mrzScanWithABBYY import scanMrzWithPi

# function will return address of stm32
def getAddress(slot):
    switcher = {
            0:0x46,
            1:0x47,
            2:0x48,
            3:0x49,
            4:0x4A,
            5:0x4B
            }
    return switcher.get(slot, None)

# this function will receive PIN-code from nextion display
# then check to server get room_number and slot
# then match slot to stm32 address and send many slot to stm32
async def checkKey():
    try:
        bus = SMBus(1)
        getkey = await client.get('t0.txt')
        await client.command('page waiting_page')
        PIN = re.sub(' ', '', getkey)
        if connect():
            rooms = key_mysql.getroom_number(PIN)
        else: #if connect to internet fail!
            await client.command('page pageWrong')

        if rooms:
            print('True')
            prev_slot = 0
            for room in rooms:
                slot = int(room[0]/22)
                if (slot>prev_slot):
                    print("255")
                    bus.i2c_rdwr(i2c_msg.write(getAddress(prev_slot), [255]))
                time.sleep(0.01)
                print(room[0])
                bus.i2c_rdwr(i2c_msg.write(getAddress(slot), [room[0]%22]))
                print("---------------------------------------- Room Number is", room[1])
                prev_slot = slot
            bus.i2c_rdwr(i2c_msg.write(getAddress(prev_slot), [255]))
            await client.command('page shRoom')
            key_mysql.setkeylog(PIN)
        else:
            print('PIN-code not correct')
            await client.command('page PinWrong')
    except NameError as e:
        print('checkKey function: ', e)

# this function prepare for read mrz in passport
async def scanPassport():
    pathfile = getFilePath()
    camera = PiCamera()
    camera.resolution = (1024, 768)
    #camera.start_preview()
    await checkPassport(pathfile, camera)
    #camera.stop_preview()
    camera.close()

# this function will loop until has passport in readBox
# then scan personal number in passport data 
# then check that to server get number room 
# then send key slot to stm32 
async def checkPassport(path, camera):
    global client
    try:
        #await client.command('tm0.en=0')
        noPP = True
        while noPP:
            if (await client.get('dp') != 5):
                raise NameError("CANCEL PRESS!")
            camera.capture(path)
            img = Image.open(path)
            f = pytesseract.image_to_string(img)
            for d in f.splitlines():
                if '<' in d:
                    noPP = False
                    break
        await client.command('page 5')
        await client.set('p5_t0.txt', "Your passport in process")
        await client.set('p5_t1.txt', "Waiting..")
        if connect():
            data = scanMrzWithPi(path)
        else: #if connect to internet fail!
            await client.command('page pageWrong')
        personNum = data.personalNum.replace("<", "")
# this is debug please comment or delete it when done
        await client.command('xstr 200,200,400,30,1,BLACK,WHITE,0,0,1,"Name: %s"' % data.name)
        await client.command('xstr 200,230,400,30,1,BLACK,WHITE,0,0,1,"Surname: '+data.surname+'"')
        await client.command('xstr 200,290,400,30,1,BLACK,WHITE,0,0,1,"Personal number: '+personNum+'"')
        await client.command('page waitting_page')
# end debug
# there is some problem to tell stm32 about slot
#        rooms = key_mysql.getroomByMRZ(personNum)
#        if rooms:
#            bus = SMBus(1)
#            prev_slot = 0
#            for room in rooms:
#                slot = int(room[0]/22)
#                if (slot>prev_slot):
#                    bus.i2c_rdwr(i2c_msg.write(getAddress(prev_slot), [-10]))
#                time.sleep(0.01)
#                bus.i2c_rdwr(i2c_msg.write(getAddress(slot), [room[0]%22]))
#                print("---------------------------------------- Room Number is", room)
#                prev_slot = slot
#            bus.i2c_rdwr(i2c_msg.write(getAddress(prev_slot), [-10]))
#            await client.command('page shRoom')
            #key_mysql.setkeylog(PIN)
#        else:
#            print("Don't have room")
#            await client.command('page pageWrong')
#            await client.set('p6_t1.txt', "Please make sure you have booked a room with the hotel.")
#            for i in range(10, 0, -1):
#                if (await client.get('dp') != 6):
#                    raise NameError('Back to standby page!')
#                await client.set('p6_tcount.txt', "This page will close in %d seconds." % i)
#                time.sleep(1)
    except NameError as e:
        print(e)
    except ValueError :
        await client.set('p5_t0.txt', "Plase insert passport agin")
        await client.set('p5_t1.txt', "Scanning..")
        await client.command('xstr 200,200,400,30,1,BLACK,8885,0,0,1,"We got some problem."')
        await checkPassport(path, camera)

# this function get event from nextion screen
def event_handler(type_, data):
    if type_ == EventType.STARTUP:
        print('We have booted up!')
    if type_ == EventType.TOUCH:
        if (data.page_id==3 and data.component_id == 42 or data.page_id==2 and data.component_id==41):
            asyncio.create_task(checkKey())
        elif (data.page_id == 4 and data.component_id == 4):
            asyncio.create_task(scanPassport())
    logging.info('Data: '+str(data))

# this function to check raspberry pi can connect to network
def connect(host='http://google.com'):
    try:
        urllib.request.urlopen(host) #Python 3.x
        return True
    except:
        return False

# initial nextion function 
async def run():
    global client
    client = Nextion('/dev/ttyAMA0', 9600, event_handler)
    await client.connect()

    # await client.sleep()
    await client.wakeup()
    
    #await client.command('sendxy=0')
    await client.command('page 0')
    await asyncio.sleep(1.5)

    if connect():
        if (await client.get('dp') != 1):
            await client.command('page stb_page')
    else: #if connect to internet fail!
        await client.command('page pageWrong')

    print('finished')

# main function
if __name__ == '__main__':
    try:
        key_mysql.servInit()
        logging.basicConfig(
            format='%(asctime)s - %(levelname)s - %(message)s',
            level=logging.DEBUG,
            handlers=[
                logging.StreamHandler()
            ])
        loop = asyncio.get_event_loop()
        asyncio.ensure_future(run())
        loop.run_forever()
    except Error as e:
        print("Error while connected to MySQL", e)
    finally:
        key_mysql.servClose()
        print("MySQL connection is closed")

