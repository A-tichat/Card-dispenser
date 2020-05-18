import asyncio, logging
import random, time, threading, re
import urllib.request
import key_mysql
from Error_checker import passportScan
from picamera import PiCamera
from mrzScanWithABBYY import scanMrzWithPi
from nextion import Nextion, EventType
from smbus2 import SMBus, i2c_msg
from mysql.connector import Error


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

async def checkKey():
    try:
        await client.command('page waiting_page')
        bus = SMBus(1)
        getkey = await client.get('t0.txt')
        PIN = re.sub(' ', '', getkey)
        rooms = key_mysql.getroom_number(PIN)
        if (rooms != None):
            print('True')
            prev_slot = 0
            for room in rooms:
                slot = int(room[0]/22)
                if (slot>prev_slot):
                    bus.i2c_rdwr(i2c_msg.write(getAddress(prev_slot), [-10]))
                time.sleep(0.01)
                bus.i2c_rdwr(i2c_msg.write(getAddress(slot), [room[0]%22]))
                print("---------------------------------------- Room Number is", room[1])
                prev_slot = slot
            #Go to show room number page
            await client.command('page shRoom')
            key_mysql.setkeylog(PIN)
        else:
            print('PIN-code not correct')
            await client.command('page PinWrong')
    except NameError:
        print('checkKey function: ', NameError)

async def scanPassport():
    global client
    pathfile = "Pictures/0.jpg"
    #camera = PiCamera()
    #camera.resolution = (1024, 768)
    #camera.start_preview()
    try:
        #camera.capture(pathfile)
        #await client.command('tm0.en=0')
        await asyncio.sleep(2)
        await client.set('p5_t1.txt', "Waiting..")
        data = scanMrzWithPi(pathfile, 60)
        await client.command('xstr 200,200,400,30,1,BLACK,WHITE,0,0,1,"Name: '+data.name+'"')
        await client.command('xstr 200,230,400,30,1,BLACK,WHITE,0,0,1,"Surname: '+data.surname+'"')
        await client.command('xstr 200,260,400,30,1,BLACK,WHITE,0,0,1,"Passport number: '+data.passportNum.replace("<","")+'"')
        await client.command('xstr 200,290,400,30,1,BLACK,WHITE,0,0,1,"Personal number: '+data.personalNum.replace("<","")+'"')
        rooms = key_mysql.getroomByMRZ(data.personalNum.replace('<',''))
        if rooms:
            for room in rooms:
                print(room, end=" ")
    except :
        #await scanPassport()
        pass
    #camera.stop_preview()
    #camera.close()
    print("Succes!!")

def event_handler(type_, data):
    if type_ == EventType.STARTUP:
        print('We have booted up!')
    if type_ == EventType.TOUCH:
        if (data.page_id==3 and data.component_id == 42 or data.page_id==2 and data.component_id==41):
            asyncio.create_task(checkKey())
        elif (data.page_id == 4 and data.component_id == 4):
            asyncio.create_task(scanPassport())
    logging.info('Data: '+str(data))

def connect(host='http://google.com'):
    try:
        urllib.request.urlopen(host) #Python 3.x
        return True
    except:
        return False

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

