from smbus2 import SMBus, i2c_msg

bus = SMBus(1)
addr = 0x70
while(True):
    value = input("Enter data: ")
    if (value.isdigit()):
        data = list()
        data.append(int(value))
        msg = i2c_msg.write(addr, data)
        bus.i2c_rdwr(msg)
    else:
        break
bus.close()
