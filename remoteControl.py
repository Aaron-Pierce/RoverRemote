"""Simple example showing how to get gamepad events."""

# from __future__ import print_function


from inputs import get_gamepad
import asyncio
import time
import socket

#print(bytearray([256-127]))

UDP_IP = None
UDP_PORT = None
with open('udp_mc_drive.conf') as configFile:
	lines = configFile.read().split("\n")
	for line in lines:
		keyValuePair = line.split("=")
		if keyValuePair[0] == "recieveip":
			UDP_IP = keyValuePair[1]
		elif keyValuePair[0] == "recieveport" or keyValuePair[0] == "receivePort":
			UDP_PORT = int(keyValuePair[1])
if not UDP_IP:
	print("Could not read recieveip from config file")
elif not UDP_PORT:
	print("Could not read recieveport from config file")
else:
	print("Going to send packets to ", (UDP_IP + ":" + str(UDP_PORT)))


sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP


def getControllerInputs():
    iters = 0
    lastInputMap = {
        "ABS_RY": 0,
        "ABS_RX": 0,
        "ABS_X": 0,
        "ABS_Y": 0
    }
    startTime = time.time() * 1000
    while 1:
        iters += 1
        if (round(time.time()*1000 - startTime)) >= 100:
#             print(lastInputMap)
             packageAndSend(lastInputMap)
             startTime = round(time.time() * 1000)
        events = get_gamepad()
        for event in events:
            if event.code in lastInputMap.keys():
                adjustedValue = event.state / 32767
                adjustedValue = 0 if abs(adjustedValue) < 0.05 else adjustedValue
                lastInputMap[event.code] = adjustedValue

def convertToTwosComplementIfNeeded(num):
    if num < 0:
        return 256+num
    else:
        return num

def packageAndSend(eventMap):
    print("Beginning")
    bytesToSend = bytearray()
#    bytesToSend.append(int(-127).to_bytes(1, byteorder="big", signed=True))
    bytesToSend.append(256-127)
    bytesToSend.append(0)
    modifiers = 0
    lWheel = convertToTwosComplementIfNeeded(int(eventMap["ABS_Y"] * 90))
    rWheel = convertToTwosComplementIfNeeded(int(eventMap["ABS_RY"] * 90))
    gimbalTilt = 0
    gimbalPan = 0
    hash = int((modifiers + lWheel + rWheel + gimbalTilt + gimbalPan) / 5)
    bytesToSend.append(modifiers)
    bytesToSend.append(lWheel)
    bytesToSend.append(rWheel)
    bytesToSend.append(gimbalTilt)
    bytesToSend.append(gimbalPan)
    bytesToSend.append(hash)
    sock.sendto(bytesToSend, (UDP_IP, UDP_PORT))
#asyncio.run(packageAndSend())
#asyncio.run(getControllerInputs())
getControllerInputs()
