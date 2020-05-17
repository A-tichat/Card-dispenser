import asyncio, logging
import random, time, threading, re
import urllib.request

from nextion import Nextion, EventType
from smbus2 import SMBus, i2c_msg

addr = list(range(0x46,0x4c))
password = {
    "room00": 0,
    "room01": 1,
    "room02": 2, 
    "room03": 3,
    "room04": 4,
    "room05": 5,
    "room06": 6, 
    "room07": 7,
    "room08": 8,
    "room09": 9,
    "room10": 10,
    "room11": 11, 
    "room12": 12,
    "room13": 13,
    "room14": 14,
    "room15": 15, 
    "room16": 16,
    "room17": 17,
    "room18": 18,
    "room19": 19,
    "room20": 20, 
    "room21": 21,
    "room22": 22,
    "room23": 23,
    "room24": 24, 
    "room25": 25,
    "room26": 26,
    "room27": 27,
    "room28": 28,
    "room29": 29, 
    "room30": 30,
    "room31": 31,
    "room32": 32,
    "room33": 33, 
    "room34": 34,
    "room35": 35,
    "room36": 36
};

async def checkKey():
    try:
        bus = SMBus(1)
        getkey = await client.get('t0.txt')
        key = re.sub(' ', '', getkey)
        if (len(key) == 6 and key in password):
            print('True')
            Room = password.get(key)
            address = addr[int(Room/18)]
            numRoom = Room%18
            bus.i2c_rdwr(i2c_msg.write(address, [numRoom]))
            print("---------------------------------------- Room Number is", numRoom)
            #Go to show room number page
            await client.command('page shRoom')
            await asyncio.sleep(0.3)
            await client.set('n0.val', numRoom)
            for i in range(10, 0, -1):
                await client.set('p4_n0.val', i)
                if (await client.get('dp') == 1):
                    print('back is press')
                    break
                elif (i == 1):
                    await asyncio.sleep(1)
                    await client.command('page 1')
                    break
                await asyncio.sleep(1)
        else:
            print('PIN-code not correct')
            await client.set('t0.txt', ' ')
    except NameError:
        print('checkKey function: ', NameError)

async def caplock():
    try:
        temp = await client.get('t0.txt')
        print(temp)
        if (await client.get('dp') == 2):
            await client.command('page 3')
        elif (await client.get('dp') == 3):
            await client.command('page 2')
        else:
            print('Error: duplicate key ID 38 or 40')
        await asyncio.sleep(0.3)
        await client.set('t0.txt',temp)
    except NameError:
        print('caplock function: ',NameError)

async def reset():
    await client.command("rest")
    time.sleep(100)


def event_handler(type_, data):
    if type_ == EventType.STARTUP:
        print('We have booted up!')
    if type_ == EventType.TOUCH:
        if data.component_id == 42:
            asyncio.create_task(checkKey())
        elif data.component_id == 40 or data.component_id == 38:
            asyncio.create_task(caplock())
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
        if (await client.get('dp') == 1):
            await client.command('page 6')
    else: #if connect to internet fail!
        await client.command('page pageWrong')

    print('finished')

if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.DEBUG,
        handlers=[
            logging.StreamHandler()
        ])
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(run())
    loop.run_forever()
