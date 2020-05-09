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
blue_safe = [0.154, 0.0806]

sys.tracebacklimit = -1
spinner = itertools.cycle(['-', '\\', '|', '/'])

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
		
class State():
	flashing = False
	current_flag = 0
	last_flag = 0
	pedal_loop = False
	is_finished = False
	
def set_color(xy):

	for l in all_lights:
		l.effect = "none"
		l.xy = xy

def lights_set_brightness(bri):
	for l in all_lights:
		l.brightness = bri

def flash_loop():
	while True:
		if state.flashing:
			for l in all_lights:
				if all_lights.index(l) % 2 == 0:
					l.brightness = 1
				else:
					l.brightness = 254
				
			time.sleep(1)
			
			for l in all_lights:
				if all_lights.index(l) % 2 == 0:
					l.brightness = 254
				else:
					l.brightness = 1
				
			time.sleep(1)

def pedal_loop():
	pass
	# while True:
		# if state.pedal_loop:
			# throttle_val = 254 * float(ir['ThrottleRaw'])
			# brake_val = 254 * float(ir['BrakeRaw'])
			# print(throttle_val)
			# print(brake_val)
			# if throttle_val > brake_val:
				# set_color(green_safe)
			# else:
				# set_color(red_safe)
			
			# for l in all_lights:
				# l.brightness = int(max(throttle_val, brake_val))
		
			

# def connect_to_iracing():

	# while not ir.startup():
			# sys.stdout.write("Waiting for iRacing ")
			# sys.stdout.write(next(spinner))
			# sys.stdout.flush()
			# sys.stdout.write("\r")

	# sys.stdout.write("iRacing Connected!")
	# sys.write("\r")
	
if __name__ == '__main__':

	config = configparser.ConfigParser(inline_comment_prefixes = (";",))
	config.read('settings.ini')

	ir = irsdk.IRSDK(parse_yaml_async = True)
	state = State()
	
	# Get variables from settings.ini
	dim_lights_after_green = bool(int(config['DEFAULT']['DimLightsAfterGreen']))
	pedal_input = bool(int(config['DEFAULT']['PedalInput']))
	light_group = config['DEFAULT']['GroupName']
	ip = config['DEFAULT']['BridgeIP']
	
	print("\nWelcome to irHUE: A small Python application for controlling Phillips Hue lights via iRacing.\nPress Ctrl-C at any time to exit the program\n")
	
	#Check if a default IP address has been specified in settings.ini
	if not ip:
		ip = input("No default IP specified!\n\nIf this is a first connection, press the blue button\non top of the Hue Bridge during the connection process.\n\nEnter Bridge IP address: ")
	
	while True:
		try:
			b = phue.Bridge(ip)
			b.connect()
			all_lights = phue.Group(b, light_group).lights
			print("Bridge found! {} lights from group {} connected.".format(len(all_lights), light_group))
			break
		except phue.PhueRequestTimeout:
			print("Could not locate bridge. Check IP address or press blue button on top of bridge during connection process")
		except LookupError:
			print("Default light group unspecified or not found, selecting all lights connected.")
			all_lights = b.lights
			print("Bridge found! {} lights connected.".format(len(all_lights)))
			break
			

	while not ir.startup():
		sys.stdout.write("Waiting for iRacing ")
		sys.stdout.write(next(spinner))
		sys.stdout.flush()
		sys.stdout.write("\r")
		time.sleep(0.1)

	for l in all_lights:
		l.transitiontime = 1.0
		l.effect = "none"

	# state.is_connected = True

	sys.stdout.write("iRacing Connected!")
	sys.stdout.flush() 

	# MAIN RACING LOOP
	
	format = "%(asctime)s: %(message)s"
	logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
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
			print(hex(state.current_flag), end="\r")

			if not state.last_flag == state.current_flag:
				print("Flag Change")
				print("Last: {}".format(hex(state.last_flag)))
				print("Current: {}".format(hex(state.current_flag)))
				
				if (state.current_flag & checkered):
					print("Checkered Flag")
					for l in all_lights:
						l.brightness = 175
						l.effect = "colorloop"
				
				elif state.current_flag & white:
					print("White Flag")
					lights_set_brightness(254)
					set_color(white_safe)

				elif state.current_flag & green:
					print("GREENFLAG")
					state.flashing = True
					lights_set_brightness(254)
					set_color(green_safe)
						
				elif state.current_flag & oneLapToGreen:
					print("One lap to green")
					state.flashing = False
					time.sleep(1.1)
					lights_set_brightness(100)
					
				elif state.current_flag & cautionWaving:
					print("Caution Waving")
					state.flashing = True
					set_color(yellow_safe)
					#lights_set_brightness(250)

				elif state.current_flag & caution:
					print("Held Caution")
					state.flashing = False
					time.sleep(1.1)
					lights_set_brightness(100)
					set_color(yellow_safe)
	
				elif state.current_flag & startHidden:
					print("Continuous green")
					state.flashing = False
					
					time.sleep(1.1)
					
					if dim_lights_after_green:
						lights_set_brightness(100)
					else:
						lights_set_brightness(254)
					
					if pedal_loop:
						state.pedal_loop = True
						
					set_color(green_safe)
				
				elif state.current_flag & black:
					print("Black Flag")
					state.flashing = True
					for l in all_lights:
						if all_lights.index(l) % 2 == 0:
							l.xy = red_safe
						else:
							l.xy = blue_safe
				else:
					print(hex(ir['SessionFlags']))

				state.last_flag = state.current_flag
				
		except KeyboardInterrupt:
			pass
		
		time.sleep(1.0)
	
	ir.shutdown()