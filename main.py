#!/usr/bin/python3
# Default library import
import asyncio
import logging
import os
import time
import re

# Installed library import
from datetime import datetime
import pytesseract
import RPi.GPIO as GPIO
from picamera import PiCamera
from PIL import Image
from nextion import Nextion, EventType

# My library import
import stm32
from googleOCR import mrzScan
from thaiId import cardScan
from api_response import *
from status_internet import *
picNum = 0
toDay = 0
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/home/pi/authenFile/key_dispenser-75e647798c48.json"

# create passport photo path
def getFilePath():
    global picNum
    global toDay
    if not os.path.isdir('./Pictures'):
        os.mkdir("Pictures")
    if datetime.today().day > toDay:
        toDay = datetime.today().day
        picNum = 1
    else:
        picNum += 1

    return "Pictures/"+datetime.today().strftime('%Y%m%d')+"_{0:04d}.png".format(picNum)


async def change_wifi_stat(network):
    if network["isChange"]:
        network["isChange"] = False
        if network["status"]:
            await client.command("stb_page.status.pic=17")
        else:
            await client.command("stb_page.status.pic=16")

# start when receive PIN-code from display
# it will connect server to get room_number and slot
# then match slot to stm32 address and send many slot to stm32


async def checkKey():
    try:
        global client
        getkey = await client.get('t0.txt')
        await client.command('page waiting_page')
        PIN = re.sub(' ', '', getkey)

        # check internet connection
        checkNet(network_connection)
        if network_connection["status"] and PIN:
            rooms = getRoom('password', PIN)
        else:
            await client.command('page pageWrong')
            await client.set('p6_t0.txt', "Can't connect to internet")
            await client.set('p6_t1.txt', "Make sure this device connect to internet correctly")
            await client.command('tm0.en=0')
            await change_wifi_stat(network_connection)
            InternetMonitor(1, network_connection, change_wifi_stat())

        if rooms:
            stm32.sendSlot(rooms)
            await client.command('page shRoom')
            resetRoom("bookNum", rooms, [])
        else:
            await client.command('page PinWrong')
    except NameError as e:
        print('checkKey function fail: ', e)


# start when display into passport scan page
# it will check has passport then capture img and decode
# if passport correct it will connect server to check and get booking_number and slot
# then match slot to stm32 address and send many slot to stm32
async def scanPassport():
    camera = PiCamera()
    try:
        path = getFilePath()
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
        await client.command('page waiting_page')
        GPIO.output(17, GPIO.LOW)

        # check internet connection
        checkNet(network_connection)
        if network_connection["status"]:
            data = mrzScan(path)
        else:
            await client.command('page pageWrong')
            await client.set('p6_t0.txt', "Can't connect to internet")
            await client.set('p6_t1.txt', "Make sure this device connect to internet correctly")
            await client.command('tm0.en=0')
            await change_wifi_stat(network_connection)
            InternetMonitor(1, network_connection, change_wifi_stat())

        rooms = getRoom('cid', data.personalNum)
        if rooms:
            stm32.sendSlot(rooms)
            GPIO.output(17, GPIO.LOW)
            await client.command('page shRoom')
            resetRoom("passport", rooms, data.personalNum, path)
        else:
            print("Don't have room")
            GPIO.output(17, GPIO.LOW)
            await client.command('page pageWrong')
            for i in range(10, 0, -1):
                if (await client.get('dp') != 6):
                    raise NameError('Back to standby page!')
                await client.set('p6_tcount.txt', "This page will close in %d seconds." % i)
                time.sleep(1)
    except NameError as e:
        print('scanPassport function fail: ', e)
    except ValueError:
        await client.command('page pageWrong')
    finally:
        GPIO.output(17, GPIO.LOW)
        if os.exits(path):
            img.close()
        camera.close()

# start when display into thai-id scan page
# it will check has thai-id for secound then decode data from card
# it will connect server to check and get booking_number and slot
# then match slot to stm32 address and send many slot to stm32


async def findId():
    global client
    try:
        tempThaiId = cardScan()
        # print(tempThaiId)
        rooms = list()
        await client.command('page waiting_page')
        # check internet connection
        checkNet(network_connection)
        if network_connection["status"]:
            rooms.extend(getRoomFromName(tempThaiId.thfullname))
            if not rooms:
                rooms.extend(getRoomFromName(tempThaiId.enfullname))
            rooms.extend(getRoom('cid', tempThaiId.cid))
        else:
            await client.command('page pageWrong')
            await client.set('p6_t0.txt', "Can't connect to internet")
            await client.set('p6_t1.txt', "Make sure this device connect to internet correctly")
            await client.command('tm0.en=0')
            await change_wifi_stat(network_connection)
            InternetMonitor(1, network_connection, change_wifi_stat())

        if rooms:
            stm32.sendSlot(rooms)
            await client.command('page shRoom')
            resetRoom("id_card", rooms, tempThaiId.cid,
                      "{}.jpg".format(tempThaiId.cid[-4:]))
        else:
            print("Not found room")
            await client.command('page pageWrong')
            for i in range(10, 0, -1):
                if (await client.get('dp') != 6):
                    raise NameError('Back to standby page!')
                await client.set('p6_tcount.txt', "This page will close in %d seconds." % i)
                time.sleep(1)
    except:
        # print("wait for card")
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
                checkNet(network_connection)
                asyncio.create_task(change_wifi_stat())
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
    client = Nextion('/dev/ttyAMA0', 115200, event_handler)
    await client.connect()

    # await client.sleep()
    await client.wakeup()

    # await client.command('sendxy=0')
    await client.command('page 0')
    await asyncio.sleep(1.5)

    checkNet(network_connection)
    if not network_connection["status"]:
        await change_wifi_stat(network_connection)
        InternetMonitor(1, network_connection, change_wifi_stat())
    if (await client.get('dp') != 1):
        await client.command('page stb_page')
    print('Boot process finished!')

# main function
if __name__ == '__main__':
    network_connection = {"status": True, "isChange": False}
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
