import asyncio
import logging
import os
import random
import time
import threading
import re

import pytesseract
import RPi.GPIO as GPIO
from picamera import PiCamera
from PIL import Image
from nextion import Nextion, EventType
from datetime import datetime

import stm32
from ManageFile import getFilePath
from mrzScanWithABBYY import scanMrzWithPi
from thaiId import cardScan
from api_response import *

# this function will receive PIN-code from nextion display
# then check to server get room_number and slot
# then match slot to stm32 address and send many slot to stm32


async def checkKey():
    try:
        getkey = await client.get('t0.txt')
        await client.command('page waiting_page')
        PIN = re.sub(' ', '', getkey)

        # check internet connection
        if connect() and PIN:
            rooms = getRoom('password', PIN)
        else:
            await client.command('page pageWrong')

        # check pin correct
        if rooms:
            stm32.sendSlot(rooms)
            await client.command('page shRoom')
            json_rooms = list(map(lambda x: {'slot': x['slot']}, rooms))
            resetRoom(json_rooms)
        else:
            await client.command('page PinWrong')
    except NameError as e:
        print('checkKey function: ', e)


# this function prepare for read mrz in passport
async def scanPassport():
    pathfile = getFilePath()
    camera = PiCamera()
    camera.resolution = (1024, 768)
    # camera.start_preview()
    await checkPassport(pathfile, camera)
    # camera.stop_preview()
    GPIO.output(17, GPIO.LOW)
    camera.close()


# this function will loop until has passport in readBox
# then scan personal number in passport data
# then check that to server get number room
# then send key slot to stm32
async def checkPassport(path, camera):
    global client
    try:
        GPIO.output(17, GPIO.HIGH)
        noPP = True
        while noPP:
            time.sleep(0.3)
            if (await client.get('dp') != 5):
                GPIO.output(17, GPIO.LOW)
                raise NameError("CANCEL PRESS!")
            camera.capture(path)
            img = Image.open(path)
            f = pytesseract.image_to_string(img)
            for d in f.splitlines():
                if '<' in d:
                    noPP = False
                    break
        await client.command('page 5')
        GPIO.output(17, GPIO.LOW)
        await client.set('p5_t0.txt', "Your passport in process")
        await client.set('p5_t1.txt', "Waiting..")

        # check internet connection
        if connect():
            data = scanMrzWithPi(path)
        else:
            await client.command('page pageWrong')
        personNum = data.personalNum.replace("<", "")

        rooms = getRoom('cid', personNum)
        if rooms:
            stm32.sendSlot(rooms)
            await client.command('page shRoom')
            json_rooms = list(map(lambda x: {'slot': x['slot']}, rooms))
            resetRoom(json_rooms)
        else:
            print("Don't have room")
            await client.command('page pageWrong')
            await client.set('p6_t1.txt', "Please make sure you have booked a room with the hotel.")
            for i in range(10, 0, -1):
                if (await client.get('dp') != 6):
                    raise NameError('Back to standby page!')
                await client.set('p6_tcount.txt', "This page will close in %d seconds." % i)
                time.sleep(1)
    except NameError as e:
        print(e)
    except ValueError:
        await client.set('p5_t0.txt', "Plase insert passport agin")
        await client.set('p5_t1.txt', "Scanning..")
        await client.command('xstr 200,200,400,30,1,BLACK,8885,0,0,1,"We got some problem."')
        if (await client.get('dp') == 5):
            await checkPassport(path, camera)


async def scanId():
    global client
    await client.command('page 5')
    await client.set('p5_t0.txt', "Please insert your Thai ID card")
    await findId()


async def findId():
    global client
    try:
        temp = cardScan()
        print(temp)
        rooms = getRoom('cid', temp.cid)
        if rooms:
            stm32.sendSlot(rooms)
            await client.command('page shRoom')
            json_rooms = list(map(lambda x: {'slot': x['slot']}, rooms))
            resetRoom(json_rooms)
        else:
            print("Don't have room")
            await client.command('page pageWrong')
            await client.set('p6_t1.txt', "Please make sure you have booked a room with the hotel.")
            for i in range(10, 0, -1):
                if (await client.get('dp') != 6):
                    raise NameError('Back to standby page!')
                await client.set('p6_tcount.txt', "This page will close in %d seconds." % i)
                time.sleep(1)
    except:
        print("wait for card")
        time.sleep(1)
        if (await client.get('dp') == 6):
            await findId()
    # await client.command('page waitting_page')


# this function get event from nextion screen
def event_handler(type_, data):
    if type_ == EventType.STARTUP:
        print('We have booted up!')
    if type_ == EventType.TOUCH:
        if (data.page_id == 3 and data.component_id == 42 or data.page_id == 2 and data.component_id == 41):
            asyncio.create_task(checkKey())
        elif (data.page_id == 4 and data.component_id == 4):
            asyncio.create_task(scanPassport())
        elif (data.page_id == 4 and data.component_id == 3):
            asyncio.create_task(scanId())
    logging.info('Data: '+str(data))


# initial nextion function
async def run():
    global client
    client = Nextion('/dev/ttyAMA0', 9600, event_handler)
    await client.connect()

    # await client.sleep()
    await client.wakeup()

    # await client.command('sendxy=0')
    await client.command('page 0')
    await asyncio.sleep(1.5)

    if connect():
        if (await client.get('dp') != 1):
            await client.command('page stb_page')
    else:  # if connect to internet fail!
        await client.command('page pageWrong')

    print('finished')


# main function
if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(17, GPIO.OUT)
    GPIO.setup(27, GPIO.OUT)
    GPIO.output(17, GPIO.LOW)
    GPIO.output(27, GPIO.HIGH)
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.DEBUG,
        handlers=[
            logging.StreamHandler()
        ])
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(run())
    loop.run_forever()
