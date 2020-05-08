
#  Raspberry Pi Master for Arduino Slave
#  i2c_master_pi.py
#  Connects to Arduino via I2C
  
#  DroneBot Workshop 2019
#  https://dronebotworkshop.com
 
from smbus import SMBus
from time import sleep
import binascii
 
addr = 0x4 # bus address
bus = SMBus(1) # indicates /dev/ic2-1
 
numb = 1
 
print ("Enter 1 for ON or 0 for OFF")
while numb == 1:
 	try:
		for i in range(0,5):
			sleep(2)
			block = bus.read_i2c_block_data(addr, 0)
			print(block)
			
	except KeyboardInterrupt:
		data = raw_input(">>>>   ")
		charString = []
		for character in data:
			charString.append(ord(character))
		bus.write_i2c_block_data(addr, 0, charString) 
		
