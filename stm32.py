import time
from smbus2 import SMBus, i2c_msg

def getAddress(slot):
    switcher = {
        0: 0x46,
        1: 0x47,
        2: 0x48,
        3: 0x49,
        4: 0x4A,
        5: 0x4B
    }
    return switcher.get(slot, None)

def sendSlot(rooms):
    bus = SMBus(1)
    prev_lot = int(rooms[0]['slot']/22)
    i=0
    j=0
    while (i < len(rooms)):
        while (j < len(rooms)):
            r = rooms[j]
            j+=1
            lot = int(r['slot']/22)
            if lot > prev_lot:
                break
            bus.i2c_rdwr(i2c_msg.write(getAddress(lot), [r['slot'] % 22]))
            time.sleep(0.01)
            print(r['slot'], end=' ')
        prev_lot = lot
        i=j
        bus.i2c_rdwr(i2c_msg.write(getAddress(prev_lot), [255]))
        print('')