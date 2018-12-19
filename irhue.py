#!python3

import irsdk, time, itertools, sys, socket
import phue
from phue import Bridge
sys.tracebacklimit = -1
spinner = itertools.cycle(['-', '/', '|', '\\'])
class State:
	ir_connected = False;

	irsdk_checkered = 0x00000001
	irsdk_white = 0x00000002
	irsdk_green = 0x00000004
	irsdk_yellow = 0x00000008
	irsdk_red = 0x00000010
	irsdk_blue = 0x00000020
	irsdk_debris = 0x00000040
	irsdk_crossed = 0x00000080
	irsdk_yellowWaving = 0x00000100
	irsdk_oneLapToGreen = 0x00000200
	irsdk_greenHeld = 0x00000400
	# irsdk_tenToGo         = 0x00000800; // not displaying this one
	# irsdk_fiveToGo        = 0x00001000; // not displaying this one
	# irsdk_randomWaving    = 0x00002000; // not displaying this one
	irsdk_caution = 0x00004000
	irsdk_cautionWaving = 0x00008000
	irsdk_black = 0x00010000
	irsdk_disqualify = 0x00020000
	# irsdk_servicible      = 0x00040000; // car is allowed service (not a flag)
	irsdk_furled = 0x00080000
	irsdk_repair = 0x00100000
	irsdk_startHidden = 0x10000000
	irsdk_startReady = 0x20000000
	irsdk_startSet = 0x40000000
	irsdk_startGo = 0x80000000
	
def check_iracing():
    if state.ir_connected and not (ir.is_initialized and ir.is_connected):
        state.ir_connected = False
        # don't forget to reset all your in State variables
        state.last_car_setup_tick = -1
        # we are shut down ir library (clear all internal variables)
        ir.shutdown()

        print('irsdk disconnected')
    elif not state.ir_connected and ir.startup() and ir.is_initialized and ir.is_connected:
        state.ir_connected = True
        caution_loop()
        print('irsdk connected')

		
		
def set_color(hue, sat):

	for l in lights:
		l.saturation = sat
		l.hue = hue
		l.brightness = 254
		
def lights_off():
	for l in lights:
		l.brightness = 1
		
def main_loop():
	
	prev_flag = ''
	flags = hex(ir['SessionFlags'])
	sys.stdout.write(flags)
	sys.stdout.flush()
	sys.stdout.write("\b\b\b\b\b\b\b\b\b\b")
	
	if not flags == prev_flag:
		if flags[9] == '4':
			set_color(25500, 200)
		elif flags[9] == '2':
			set_color(11111, 0)
		elif (flags[6] == '8' or flags[6] == '4') and (flags[7] == '0'):
			set_color(11200, 200)
			caution_loop()
		else:
			lights_off()
	
	
#0x10000000
#268435456 = green flag racing (pedal loop)

#0x10000004
#268435460 = green flag start (all green)
	
def caution_loop():
	
		for l in lights:
			l.brightness = 254
			#time.sleep(3/4)
		
		for l in lights:
			l.brightness = 0
			#time.sleep(3/4)
	

if __name__ == '__main__':
	
	ir = irsdk.IRSDK(parse_yaml_async=True)
	state = State()
	sleep_time = 0.1
	
	print("\nWelcome to irHUE: A small python application for controlling Phillips Hue lights via iRacing.\nPress ctrl-c at any time to exit the program\n")
	
	while True:
	
		ip = input("Enter Bridge IP address: ")

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
				main_loop()
				
			else:
				sys.stdout.write("Waiting for iRacing ")
				sys.stdout.write(next(spinner))
				sys.stdout.flush()
				sys.stdout.write('\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b')
			# sleep for 1 second
			# maximum you can use is 1/60
			# cause iracing update data with 60 fps
			time.sleep(sleep_time)
	except KeyboardInterrupt:
	# press ctrl+c to exit
		pass