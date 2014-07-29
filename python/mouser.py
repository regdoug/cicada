import mouse
import cicada
import serial
from time import sleep
from datetime import datetime

class Mouser(object):


    m = mouse.Mouse()
    
    def __init__(self):
        self.ser = serial.Serial('COM3', 9600)
        self.c = cicada.Cicada(self.ser)
        self.dt = datetime.now()
        self.c.add_observer(self.event)      

    def event(self,type,index,state):
        pass
    

def main():

    m = Mouser()
    
    while True:
        if m.ser.inWaiting()>0:
            byte = m.ser.read()
            m.c.update(byte)
                
        if m.c[7].button==1:
            old_pos = m.m.get_position()
            new_pos = (old_pos[0],old_pos[1]-1)
            m.m.move_mouse(new_pos)
    
        sleep(0.01)
        
if __name__ == "__main__":
    main()