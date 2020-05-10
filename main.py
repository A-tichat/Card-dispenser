import asyncio
import logging
import random
import time
import re

from nextion import Nextion, EventType
from smbus2 import SMBus, i2c_msg

addr = 0x70
password = {
    "room01": 1,
    "room02": 2,
    "room03": 3,
    "room04": 4,
    "room05": 5,
    "room06": 6,
    "room07": 7,
    "room08": 8,
    "room09": 9
};

async def checkKey():
    try:
        bus = SMBus(1)
        getkey = await client.get('t0.txt')
        key = re.sub(' ', '', getkey)
        if (len(key) == 6 and key in password):
            print('True')
            numRoom = password.get(key)
            bus.i2c_rdwr(i2c_msg.write(addr, [numRoom]))
            await client.command('page 4')
            await asyncio.sleep(0.3)
            for i in range(10, 0, -1):
                await client.set('p4_n0.val', i)
                await asyncio.sleep(1)
            await client.command('page 6')
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
            print('False')
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
    

def event_handler(type_, data):
    if type_ == EventType.STARTUP:
        print('We have booted up!')
    elif type_ == EventType.TOUCH:
        if data.component_id == 42:
            asyncio.create_task(checkKey())
        elif data.component_id == 40 or data.component_id == 38:
            asyncio.create_task(caplock())
    logging.info('Data: '+str(data))

async def run():
    global client
    client = Nextion('/dev/ttyAMA0', 9600, event_handler)
    await client.connect()

    # await client.sleep()
    await client.wakeup()
    
    #await client.command('sendxy=0')
    await client.command('page 0')
    await asyncio.sleep(1.5)

    if (await client.get('dp') != 1):
        await client.command('page 1')

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
