import asyncio
import logging
import os
import random
import time
import re
import socket

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


async def change_stat():
    global myconnect
    myconnect=not myconnect
    if myconnect:
        await client.command("stb_page.status.pic=17")
    else:
        await client.command("stb_page.status.pic=16")


# this function will receive PIN-code from nextion display
# then check to server get room_number and slot
# then match slot to stm32 address and send many slot to stm32
async def checkKey():
    try:
        global client
        getkey = await client.get('t0.txt')
        await client.command('page waiting_page')
        PIN = re.sub(' ', '', getkey)

        # check internet connection
        if connect() and PIN:
            rooms = getRoom('password', PIN)
        else:
            await client.command('page pageWrong')
            await client.set('p6_t0.txt', "Can't connect to internet")
            await client.set('p6_t1.txt', "Make sure this device connect to internet correctly")
            await client.command('tm0.en=0')

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
    try:
        path = getFilePath()
        camera = PiCamera()
        camera.resolution = (1024, 768)
        global client
        GPIO.output(17, GPIO.HIGH)
        noPP = True
        while noPP:
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
        await client.command('page passportScan')
        GPIO.output(17, GPIO.LOW)

        # check internet connection
        if connect():
            data = scanMrzWithPi(path)
        else:
            await client.command('page pageWrong')
            await client.set('p6_t0.txt', "Can't connect to internet")
            await client.set('p6_t1.txt', "Make sure this device connect to internet correctly")
            await client.command('tm0.en=0')
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
            for i in range(10, 0, -1):
                if (await client.get('dp') != 6):
                    raise NameError('Back to standby page!')
                await client.set('p6_tcount.txt', "This page will close in %d seconds." % i)
                time.sleep(1)
    except NameError as e:
        print(e)
    except ValueError:
        await client.command('page pageWrong')
    finally:
        camera.close()


async def findId():
    global client
    try:
        tempThaiId = cardScan()
        print(tempThaiId)
        rooms = getRoom('cid', tempThaiId.cid)
        rooms.extend(sendName(tempThaiId.thfullname))
        if not rooms:
            rooms.extend(sendName(tempThaiId.enfullname))
        if rooms:
            stm32.sendSlot(rooms)
            await client.command('page shRoom')
            json_rooms = list(map(lambda x: {'slot': x['slot']}, rooms))
            resetRoom(json_rooms)
        else:
            print("Don't have room")
            await client.command('page pageWrong')
            for i in range(10, 0, -1):
                if (await client.get('dp') != 6):
                    raise NameError('Back to standby page!')
                await client.set('p6_tcount.txt', "This page will close in %d seconds." % i)
                time.sleep(1)
    except:
        print("wait for card")
        time.sleep(1)
        if (await client.get('dp') == 10):
            await findId()
    # await client.command('page waitting_page')


# this function get event from nextion screen
def event_handler(type_, data):
    if type_ == EventType.STARTUP:
        print('We have booted up!')
    if type_ == EventType.TOUCH:
        if (data.page_id == 1):
            if (data.component_id == 3):
                asyncio.create_task(change_stat())
        elif (data.page_id == 2):
            if (data.component_id == 41):
                asyncio.create_task(checkKey())
        elif (data.page_id == 3):
            if (data.component_id == 42):
                asyncio.create_task(checkKey())
        elif (data.page_id == 4):
            if (data.component_id == 3):
                asyncio.create_task(scanPassport())
            elif (data.component_id == 2):
                asyncio.create_task(findId())
    # logging.info('Data: '+str(data))


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

    if (await client.get('dp') != 1):
        await client.command('page stb_page')
    print('finished')


# main function
if __name__ == '__main__':
    myconnect = True
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(17, GPIO.OUT)
    GPIO.output(17, GPIO.LOW)
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.DEBUG,
        handlers=[
            logging.StreamHandler()
        ])
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(run())
    loop.run_forever()
