#!python3

#	#	#	#	#	#	#	#	#	#	#	#	#	#
#  __  .______       __    __   __    __   _______ 	#
# |  | |   _  \     |  |  |  | |  |  |  | |   ____|	#
# |  | |  |_)  |    |  |__|  | |  |  |  | |  |__   	#
# |  | |      /     |   __   | |  |  |  | |   __|  	#
# |  | |  |\  \----.|  |  |  | |  `--'  | |  |____ 	#
# |__| | _| `._____||__|  |__|  \______/  |_______|	#
#													#
#	#	#	#	#	#	#	#	#	#	#	#	#	#

'''
Welcome to irHUE, a program to connect iRacing to a Phillips Hue System

Author: Daniel Knight
'''

import irsdk
import time
import itertools
import sys
import socket
import configparser
import phue
import math
import threading

# RGB colors that fit into HUE Gamut
yellow_safe = [0.4119, 0.5157]
green_safe = [0.2075, 0.6549]

sys.tracebacklimit = -1
spinner = itertools.cycle(['-', '/', '|', '\\'])

# Flag Codes
checkered = 0x00000001
white = 0x00000002
green = 0x00000004
yellow = 0x00000008
red = 0x00000010
blue = 0x00000020
debris = 0x00000040
crossed = 0x00000080
yellowWaving = 0x00000100
oneLapToGreen = 0x00000200
greenHeld = 0x00000400
caution = 0x00004000
cautionWaving = 0x00008000
black = 0x00010000
disqualify = 0x00020000
furled = 0x00080000
repair = 0x00100000
startHidden = 0x10000000
startReady = 0x20000000
startSet = 0x40000000
startGo = 0x80000000

class State:
	ir_connected = False;


def is_inside_gamut(x, y):

	x1 = 0.675
	y1 = 0.322
	x2 = 0.4091
	y2 = 0.518
	x3 = 0.167
	y3 = 0.04
	
	c1 = (x2 - x1) * (y - y1) - (y2 - y1) * (x - x1)
	c2 = (x3 - x2) * (y - y2) - (y3 - y2) * (x - x2)
	c3 = (x1 - x3) * (y - y3) - (y1 - y3) * (x - x3)
	
	if (c1 < 0 and c2 < 0 and c3 < 0) or (c1 > 0 and c2 > 0 and c3 > 0):
		return True
	else:
		return False

def rgb_to_xy(rgb):

	for color in rgb:
		color = color / 255
		color = pow((color + 0.055) / 1.055, 2.4) if color > 0.04045 else color / 12.92
		
	X = rgb[0] * 0.649926 + rgb[1] * 0.103455 + rgb[2] * 0.197109
	Y = rgb[0] * 0.234327 + rgb[1] * 0.743075 + rgb[2] * 0.022598
	Z = rgb[0] * 0.000000 + rgb[1] * 0.053077 + rgb[2] * 1.035763
	
	x = X / (X + Y + Z)
	y = Y / (X + Y + Z)
	
	if is_inside_gamut(x, y):
		return x, y, Y
		
	else:
		return 0.0, 0.0, 0.0	
		
def set_color(xy):

	for l in lights:
		l.xy = xy

		
def lights_off():
	for l in lights:
		l.brightness = 1
		
def main_loop(blink, dim):
	
	prev_flag = 0
	flag = hex(ir['SessionFlags'])
	flag = int(flag, 16)
	print(hex(ir['SessionFlags']))
	sys.stdout.write(hex(flag))
	sys.stdout.flush()
	sys.stdout.write("\r")
	

	if not flag == prev_flag:
		if flag & (irsdk_green or irsdk_greenHeld):
			print("Green")
			
		elif flag & irsdk_white:
			print("White")

		elif flag & irsdk_cautionWaving:
			#set_color(yellow_safe)
			print("Yellow Waving")
			if blink == 1:
				blink_loop()

		elif flag & irsdk_caution:
			print("Yellow")
			#set_color(yellow_safe)
			
		elif flag & irsdk_oneLapToGreen:
			print("One to Go")
		else:
			if dim == 1:
				print("DIM")
				#lights_off()

	prev_flag = flag
	
def blink_loop():
	
		for l in lights:
			l.brightness = 254
		
		for l in lights:
			l.brightness = 0

def connect_to_iracing():

	while not ir.startup():
			sys.stdout.write("Waiting for iRacing ")
			sys.stdout.write(next(spinner))
			sys.stdout.flush()
			sys.stdout.write("\r")
	
	""" OLD CODE
    if state.ir_connected and not (ir.is_initialized and ir.is_connected):
        state.ir_connected = False
        # don't forget to reset all your in State variables
        state.last_car_setup_tick = -1
        # we shut down ir library (clear all internal variables)
        ir.shutdown()

        print('irsdk disconnected')
    elif not state.ir_connected and ir.startup() and ir.is_initialized and ir.is_connected:
        state.ir_connected = True
        print('irsdk connected')
	"""

def main():

	print("\nWelcome to irHUE: A small Python application for controlling Phillips Hue lights via iRacing.\nPress Ctrl-C at any time to exit the program\n")
	
	#Check if a default IP address has been specified in settings.ini
	if not default_ip:
		ip = input("No default IP specified!\n\nIf this is a first connection, press the blue button\non top of the Hue Bridge during the connection process.\n\nEnter Bridge IP address: ")
	
	while True:
		try:
			b = phue.Bridge(ip)
			b.connect()
			all_lights = b.lights
			print("Bridge found! {} lights connected.".format(len(all_lights)))
			break
		except (phue.PhueRequestTimeout):
			print("Could not locate bridge. Check IP address or press blue button on top of bridge during connection process")
			
	iRacingConnectionThread = threading.Thread(target=check_iracing)
	iRacingConnectionThread.start()
	
if __name__ == '__main__':
	
	config = configparser.ConfigParser(inline_comment_prefixes = (";",))
	config.read('settings.ini')
	
	ir = irsdk.IRSDK(parse_yaml_async = True)
	state = State()
	
	dim_lights_after_green = config['DEFAULT']['DimLightsAfterGreen']
	ip = config['DEFAULT']['BridgeIP']
	
	main()
	
	""" START OLD CODE
	prev_flag = 0
	config = configparser.ConfigParser()
	config.read('settings.ini')
	ir = irsdk.IRSDK(parse_yaml_async=True)
	state = State()
	sleep_time = 0.1
	blink = config['DEFAULT']['BlinkCautionLights']
	dim = config['DEFAULT']['DimLights']
	
	print("\nWelcome to irHUE: A small python application for controlling Phillips Hue lights via iRacing.\nPress ctrl-c at any time to exit the program\n")
	
	while True:
	
		if len(config['DEFAULT']['BridgeIP']) == 0:
			ip = input("No default IP specified!\n\nIf this is a first connection, press the blue button\non top of the Hue Bridge during the connection process.\n\nEnter Bridge IP address: ")
		else:
			ip = config['DEFAULT']['BridgeIP']

		print("Attempting bridge connection...")
	
		try:
			b = Bridge(ip)
			b.connect()
			lights = b.lights
			print("Bridge found! {} lights connected.".format(len(lights)))
			break
		except (phue.PhueRequestTimeout):
			print("Could not locate bridge. Check IP address or press blue button on top of bridge during connection process")
	
	try:
	# infinite loop
		while True:
		# check if we are connected to iracing
			# if we are, then process data
			check_iracing()
			
			if state.ir_connected:
				
				sleep_time = 1
				main_loop(blink, dim)
				
			else:
				sys.stdout.write("Waiting for iRacing ")
				sys.stdout.write(next(spinner))
				sys.stdout.flush()
				sys.stdout.write("\r")
			# sleep for 1 second
			# maximum you can use is 1/60
			# cause iracing updates data with 60 fps
			time.sleep(sleep_time)
	except KeyboardInterrupt:
	# press ctrl+c to exit
		pass
		
	"""