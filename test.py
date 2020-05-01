import irsdk, time, itertools, sys, socket, configparser, phue, math
from phue import Bridge

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

	for i in range(len(rgb)):
		rgb[i] = rgb[i] / 255
		rgb[i] = pow((rgb[i] + 0.055) / 1.055, 2.4) if rgb[i] > 0.04045 else rgb[i] / 12.92
		
	X = rgb[0] * 0.649926 + rgb[1] * 0.103455 + rgb[2] * 0.197109
	Y = rgb[0] * 0.234327 + rgb[1] * 0.743075 + rgb[2] * 0.022598
	Z = rgb[0] * 0.000000 + rgb[1] * 0.053077 + rgb[2] * 1.035763
	
	x = X / (X + Y + Z)
	y = Y / (X + Y + Z)
	
	print(x, y)
	
	if is_inside_gamut(x, y):
		return x, y, Y
		
	else:
		return 0.0, 0.0, 0.0
		

def main():
	while True:
		r = float(input("r"))
		g = float(input("g"))
		b = float(input("B"))
		rgb = [r, g, b]
		print(rgb_to_xy(rgb))
		

if __name__ == '__main__':
	main()