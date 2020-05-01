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
import urllib
import logging

# RGB colors that fit into HUE Gamut
yellow_safe = [0.4934, 0.4571]
green_safe = [0.2075, 0.6549]
white_safe = [0.3, 0.3]
red_safe = [0.6818, 0.3071]

sys.tracebacklimit = -1
spinner = itertools.cycle(['-', '/', '|', '\\'])

all_lights = None

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

# class State(object):
		
	# def __init__(self):
		# print ('Processing current state:', str(self))

	# def update(self):
		# """
		# Handle Events
		# """
		# pass
		
	# def __repr__(self):
		# """
		# Leverages the __str__ method to describe the State
		# """
		# return self.__str__()
	
	# def __str__(self):
		# """
		# Returns the name of the State.
		# """
		# return self.__class__.__name__
		
# class Green(State):
	
	# def __init__(self, flashing):
		# self.flashing = flashing
		# self.color = green_safe
	
		
	# def update(self):
		# if self.flashing:
			# flash_loop()
		# return self

		
# class StateManager(object):
	# """
	# Simple state manager for flag states
	# """
	
	# current_flag = 0
	
	# def __init__(self, dim_lights):
		# """ Initialize Components """
		# self.state = Green(flashing = False)
		# self.dim_lights = dim_lights
		
	# def update(self):
		
		# self.state.update()
		
class State():
	flashing = False
	current_flag = 0
	last_flag = 0
	
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

	for l in all_lights:
		l.xy = xy

def lights_set_brightness(bri):
	for l in all_lights:
		l.brightness = bri

	
def flash_loop():
	while True:
		if state.flashing:
			for l in all_lights:
				l.brightness = 254
				
			time.sleep(1)
			
			for l in all_lights:
				l.brightness = 0

def pedal_loop():
	while True:
		throttle_val = 254 * float(ir['ThrottleRaw'])
		brake_val = 254 * float(ir['BrakeRaw'])
		print(throttle_val)
		print(brake_val)
		if throttle_val > brake_val:
			set_color(green_safe)
		else:
			set_color(red_safe)
		
		for l in all_lights:
			l.brightness = int(max(throttle_val, brake_val))
		
			

# def connect_to_iracing():

	# while not ir.startup():
			# sys.stdout.write("Waiting for iRacing ")
			# sys.stdout.write(next(spinner))
			# sys.stdout.flush()
			# sys.stdout.write("\r")

	# sys.stdout.write("iRacing Connected!")
	# sys.write("\r")
	
if __name__ == '__main__':

	format = "%(asctime)s: %(message)s"
	logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
	config = configparser.ConfigParser(inline_comment_prefixes = (";",))
	config.read('settings.ini')

	ir = irsdk.IRSDK(parse_yaml_async = True)
	state = State()
	
	dim_lights_after_green = bool(int(config['DEFAULT']['DimLightsAfterGreen']))
	ip = config['DEFAULT']['BridgeIP']
	
	print("\nWelcome to irHUE: A small Python application for controlling Phillips Hue lights via iRacing.\nPress Ctrl-C at any time to exit the program\n")
	
	#Check if a default IP address has been specified in settings.ini
	if not ip:
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

	while not ir.startup():
		sys.stdout.write("Waiting for iRacing ")
		sys.stdout.write(next(spinner))
		sys.stdout.flush()
		sys.stdout.write("\r")
		time.sleep(0.1)

	for l in all_lights:
		l.transitiontime = 1.0

	# state.is_connected = True

	sys.stdout.write("iRacing Connected!")
	sys.stdout.flush()
	sys.stdout.write("\r")

	# MAIN RACING LOOP
	
	logging.info("Main		: before creating thread")
	FlashLoopThread = threading.Thread(target=flash_loop, daemon=True)
	PedalLoopThread = threading.Thread(target=pedal_loop, daemon=True)
	logging.info("Main		: before running thread")
	FlashLoopThread.start()
	PedalLoopThread.start()
	logging.info("Main		: wait for thread to finish")

	
	
	while True:

		try:
			if not ir.is_connected:
				break
				
			state.current_flag = int(hex(ir['SessionFlags']), 16)
			print(hex(state.current_flag))
			print(state.current_flag)
			print(state.last_flag)

			if not state.last_flag == state.current_flag:

				if state.current_flag & green:
					print("GREENFLAG")
					state.flashing = True
					#lights_set_brightness(254)
					set_color(green_safe)
					
					
				elif state.current_flag & oneLapToGreen:
					print("One to Go")
					state.flashing = False
					lights_set_brightness(250)
					set_color(white_safe)
					
					
					
				elif state.current_flag & cautionWaving:
					print("Caution Waving")
					state.flashing = True
					set_color(yellow_safe)
					#lights_set_brightness(250)
					
					
				elif state.current_flag & caution:
					print("Held Caution")
					state.flashing = False
					lights_set_brightness(250)
					set_color(yellow_safe)
					
					
					
				elif state.current_flag & startHidden:
					print("Continuous green")
					state.flashing = False
					
					if dim_lights_after_green:
						lights_set_brightness(1)
					else:
						lights_set_brightness(254)
						
					set_color(green_safe)
				else:
					print(hex(ir['SessionFlags']))

				state.last_flag = state.current_flag
				
				
		except KeyboardInterrupt:
			pass
		
		time.sleep(1.0)
	
	ir.shutdown()
