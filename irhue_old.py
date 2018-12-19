#!python3

import irsdk
from phue import Bridge

b = Bridge(#"BRIDGE_IP_HERE")

b.connect()

lights = b.lights

class State:
	ir_connected = False;

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
        print('irsdk connected')
		
		
		
def set_color(hue):

	for l in lights:
		l.saturation = 200
		l.hue = hue
		l.brightness = 254
		
def lights_off():
	for l in lights:
		l.brightness = 1
		
def main_loop():
	
	
	flags = hex(ir['SessionFlags'])
	
	print(flags)
	
	#Green Flag!
	if flags[9] == '4':
		set_color(25500)
	
	#Caution Flag, One Lap to Green, Race Start
	elif (flags[6] == '8' or flags[6] == '4') and (flags[7] == '0'):
		set_color(12750)
		caution_loop()
	
	else:
		lights_off()
	
	
#0x10000000
#268435456 = green flag racing (pedal loop)

#0x10000004
#268435460 = green flag start (all green)
	
def caution_loop():
	
		lights[1].brightness = 254
		lights[0].brightness = 0
		lights[2].brightness = 0
		
		time.sleep(3/4)
		
		lights[1].brightness = 0
		lights[0].brightness = 254
		lights[2].brightness = 254
		
		time.sleep(3/4)
	

if __name__ == '__main__':
	
	ir = irsdk.IRSDK(parse_yaml_async=True)
	state = State()
	
	try:
	# infinite loop
		while True:
		# check if we are connected to iracing
			check_iracing()
			# if we are, then process data
			if state.ir_connected:
				
				main_loop()
				
			# sleep for 1 second
			# maximum you can use is 1/60
			# cause iracing update data with 60 fps
			time.sleep(1)
	except KeyboardInterrupt:
	# press ctrl+c to exit
		pass