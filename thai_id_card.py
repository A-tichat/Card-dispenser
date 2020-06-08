#!/usr/bin/env python
# bouroo<bouroo@gmail.com>
# 07.04.2019
# sudo apt-get -y install pcscd python-pyscard python-pil

import binascii
import io
import os
import sys
from PIL import Image
from smartcard.System import readers
from smartcard.util import HexListToBinString, toHexString, toBytes

# Thailand ID Smartcard
class idCardScan:
	# tis-620 to utf-8
	# define the APDUs used in this script
	# https://github.com/chakphanu/ThaiNationalIDCard/blob/master/APDU.md

	def __init__(self):
		# Check card
		SELECT = [0x00, 0xA4, 0x04, 0x00, 0x08]
		THAI_CARD = [0xA0, 0x00, 0x00, 0x00, 0x54, 0x48, 0x00, 0x01]

		# CID
		CMD_CID = [0x80, 0xb0, 0x00, 0x04, 0x02, 0x00, 0x0d]

		# TH Fullname
		CMD_THFULLNAME = [0x80, 0xb0, 0x00, 0x11, 0x02, 0x00, 0x64]

		# EN Fullname
		CMD_ENFULLNAME = [0x80, 0xb0, 0x00, 0x75, 0x02, 0x00, 0x64]

		# Date of birth
		CMD_BIRTH = [0x80, 0xb0, 0x00, 0xD9, 0x02, 0x00, 0x08]

		# Gender
		CMD_GENDER = [0x80, 0xb0, 0x00, 0xE1, 0x02, 0x00, 0x01]

		# Card Issuer
		CMD_ISSUER = [0x80, 0xb0, 0x00, 0xF6, 0x02, 0x00, 0x64]

		# Issue Date
		CMD_ISSUE = [0x80, 0xb0, 0x01, 0x67, 0x02, 0x00, 0x08]

		# Expire Date
		CMD_EXPIRE = [0x80, 0xb0, 0x01, 0x6F, 0x02, 0x00, 0x08]

		# Address
		CMD_ADDRESS = [0x80, 0xb0, 0x15, 0x79, 0x02, 0x00, 0x64]

		# Photo_Part1/20
		CMD_PHOTO1 = [0x80, 0xb0, 0x01, 0x7B, 0x02, 0x00, 0xFF]

		# Photo_Part2/20
		CMD_PHOTO2 = [0x80, 0xb0, 0x02, 0x7A, 0x02, 0x00, 0xFF]

		# Photo_Part3/20
		CMD_PHOTO3 = [0x80, 0xb0, 0x03, 0x79, 0x02, 0x00, 0xFF]

		# Photo_Part4/20
		CMD_PHOTO4 = [0x80, 0xb0, 0x04, 0x78, 0x02, 0x00, 0xFF]

		# Photo_Part5/20
		CMD_PHOTO5 = [0x80, 0xb0, 0x05, 0x77, 0x02, 0x00, 0xFF]

		# Photo_Part6/20
		CMD_PHOTO6 = [0x80, 0xb0, 0x06, 0x76, 0x02, 0x00, 0xFF]

		# Photo_Part7/20
		CMD_PHOTO7 = [0x80, 0xb0, 0x07, 0x75, 0x02, 0x00, 0xFF]

		# Photo_Part8/20
		CMD_PHOTO8 = [0x80, 0xb0, 0x08, 0x74, 0x02, 0x00, 0xFF]

		# Photo_Part9/20
		CMD_PHOTO9 = [0x80, 0xb0, 0x09, 0x73, 0x02, 0x00, 0xFF]

		# Photo_Part10/20
		CMD_PHOTO10 = [0x80, 0xb0, 0x0A, 0x72, 0x02, 0x00, 0xFF]

		# Photo_Part11/20
		CMD_PHOTO11 = [0x80, 0xb0, 0x0B, 0x71, 0x02, 0x00, 0xFF]

		# Photo_Part12/20
		CMD_PHOTO12 = [0x80, 0xb0, 0x0C, 0x70, 0x02, 0x00, 0xFF]

		# Photo_Part13/20
		CMD_PHOTO13 = [0x80, 0xb0, 0x0D, 0x6F, 0x02, 0x00, 0xFF]

		# Photo_Part14/20
		CMD_PHOTO14 = [0x80, 0xb0, 0x0E, 0x6E, 0x02, 0x00, 0xFF]

		# Photo_Part15/20
		CMD_PHOTO15 = [0x80, 0xb0, 0x0F, 0x6D, 0x02, 0x00, 0xFF]

		# Photo_Part16/20
		CMD_PHOTO16 = [0x80, 0xb0, 0x10, 0x6C, 0x02, 0x00, 0xFF]

		# Photo_Part17/20
		CMD_PHOTO17 = [0x80, 0xb0, 0x11, 0x6B, 0x02, 0x00, 0xFF]

		# Photo_Part18/20
		CMD_PHOTO18 = [0x80, 0xb0, 0x12, 0x6A, 0x02, 0x00, 0xFF]

		# Photo_Part19/20
		CMD_PHOTO19 = [0x80, 0xb0, 0x13, 0x69, 0x02, 0x00, 0xFF]

		# Photo_Part20/20
		CMD_PHOTO20 = [0x80, 0xb0, 0x14, 0x68, 0x02, 0x00, 0xFF]

		# Get all the available readers
		readerList = readers()
		print("Available readers:")
		for readerIndex,readerItem in enumerate(readerList):
			print(readerIndex, readerItem)

		# Select reader
		readerSelectIndex = 0 #int(input("Select reader[0]: ") or "0")

		reader = readerList[readerSelectIndex]
		print("Using:", reader)

		connection = reader.createConnection()
		connection.connect()
		atr = connection.getATR()
		print("ATR: " + toHexString(atr))
		if (atr[0] == 0x3B & atr[1] == 0x67):
			req = [0x00, 0xc0, 0x00, 0x01]
		else :
			req = [0x00, 0xc0, 0x00, 0x00]

		# Check card
		data, sw1, sw2 = connection.transmit(SELECT + THAI_CARD)
		print("Select Applet: %02X %02X" % (sw1, sw2))

		# CID
		self.cid = thai2unicode(getData(CMD_CID, req)[0])
		# TH Fullname
		self.thFullname = thai2unicode(getData(CMD_THFULLNAME, req)[0])
		# EN Fullname
		self.enFullname = thai2unicode(getData(CMD_ENFULLNAME, req)[0])
		# Date of birth
		self.dob = thai2unicode(getData(CMD_BIRTH, req)[0])
		# Gender
		self.gender = thai2unicode(getData(CMD_GENDER, req)[0])
		# Card Issuer
		self.cardIssuer = thai2unicode(getData(CMD_ISSUER, req)[0])
		# Issue Date
		self.issueDate = thai2unicode(getData(CMD_ISSUE, req)[0])
		# Expire Date
		self.expireDate = thai2unicode(getData(CMD_EXPIRE, req)[0])
		# Address
		self.address = thai2unicode(getData(CMD_ADDRESS, req)[0])
		# PHOTO
		photo = getData(CMD_PHOTO1, req)[0]
		photo += getData(CMD_PHOTO2, req)[0]
		photo += getData(CMD_PHOTO3, req)[0]
		photo += getData(CMD_PHOTO4, req)[0]
		photo += getData(CMD_PHOTO5, req)[0]
		photo += getData(CMD_PHOTO6, req)[0]
		photo += getData(CMD_PHOTO7, req)[0]
		photo += getData(CMD_PHOTO8, req)[0]
		photo += getData(CMD_PHOTO9, req)[0]
		photo += getData(CMD_PHOTO10, req)[0]
		photo += getData(CMD_PHOTO11, req)[0]
		photo += getData(CMD_PHOTO12, req)[0]
		photo += getData(CMD_PHOTO13, req)[0]
		photo += getData(CMD_PHOTO14, req)[0]
		photo += getData(CMD_PHOTO15, req)[0]
		photo += getData(CMD_PHOTO16, req)[0]
		photo += getData(CMD_PHOTO17, req)[0]
		photo += getData(CMD_PHOTO18, req)[0]
		photo += getData(CMD_PHOTO19, req)[0]
		photo += getData(CMD_PHOTO20, req)[0]
		data = HexListToBinString(photo)
		f = open(cid + ".jpg", "wb")
		f.write(data)
		f.close

	def printData(self):
		print("CID: " + self.cid)
		print("TH Fullname: " + self.thFullname)
		print("EN Fullname: " + self.enFullname)
		print("Date of birth: " + self.dob)
		print("Gender: " + self.gender)
		print("Card Issuer: " + self.cardIssuer)
		print("Issue Date: " + self.issueDate)
		print("Expire Date: " + self.expireDate)
		print("Address: " + self.address)

def thai2unicode(data):
	result = ''
	if isinstance(data, list):
		for d in data:
			if (sys.version_info.major < 3):
				result += unicode(chr(d),"tis-620")
			else :
				result += chr(d).decode("tis-620").encode("utf-8")
	else :
		result = data.decode("tis-620").encode("utf-8")
	return result.strip()

def getData(cmd, req = [0x00, 0xc0, 0x00, 0x00]):
	data, sw1, sw2 = connection.transmit(cmd)
	data, sw1, sw2 = connection.transmit(req + [cmd[-1]])
	return [data, sw1, sw2]
