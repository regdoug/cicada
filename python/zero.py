import cicada
import serial
from time import sleep
from datetime import datetime

class Zero(object):

	armed = False
	green = False
	
	def __init__(self):
		self.ser = serial.Serial('COM3', 9600)
		self.c = cicada.Cicada(self.ser)
		self.dt = datetime.now()
		self.c.add_observer(self.event)
		

	def event(self,type,index,state):
		if self.armed and state == 1:
			if index == 4:
				self.c.tare()
				self.c[4].set_color((0,254,0))
				self.dt = datetime.now()
				self.green = True
			self.armed = False
			

def main():
	z = Zero()
	try:
		while True:
			if z.ser.inWaiting()>0:
				byte = z.ser.read()
				print(byte)
				z.c.update(byte)
			
			if z.c[4].press_seconds()>4:
				z.c[4].set_color((254,0,0))
				z.armed = True
				z.dt = datetime.now()
				
			if z.green and z.dt is not None and ((datetime.now()-z.dt).seconds)>4:
				z.c[4].set_color((254,254,254))
				z.dt = None
				
			if z.armed and z.dt is not None and ((datetime.now()-z.dt).seconds)>4:
				z.armed = False
				z.c.set_all_colors((254,254,254))
				z.dt = None
				
			sleep(0.01)
	finally:
		z.ser.close()
		
if __name__ == "__main__":
	main()