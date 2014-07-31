import mouse
import cicada
import serial
from time import sleep
from datetime import datetime

class Mouser(object):

    init_done = False
    color = [(0,0,254),(0,254,254),(0,0,254),(0,254,254),(254,0,254),(0,254,254),(0,0,0),(0,254,254),(0,0,0)]
    position = [27,25,27,25,0,25,0,25,0]
    
    def __init__(self):
        self.ser = serial.Serial('COM3', 9600)
        self.c = cicada.Cicada(self.ser)
        self.dt = datetime.now()
        self.c.add_observer(self.event)

    def event(self,type,index,state):
        if not self.init_done:
            if index == 8 and state == 0:
                for i in range(9):
                    self.c[i].set_color(self.color[i])
                    self.c[i].go_to(self.position[i],205)
        if index in [0,1,2,3,4,5,7]:
            color = (254,0,0) if state == 1 else self.color[index]
            self.c[index].set_color(color)
        if index == 0 and self.init_done:
            mouse.release() if state == 0 else mouse.hold()
        if index == 2 and self.init_done:
            mouse.rightrelease() if state == 0 else mouse.righthold()
        if index == 4 and self.init_done:
            mouse.middlerelease() if state == 0 else mouse.middlehold()


def main():

    m = Mouser()
    hold = False
    righthold = False
    middlehold = False
    
    def shutdown():
        for i in range(9):
            m.c[i].go_to(0,205)
            sleep(0.1)
    
    while True:
    
        if m.ser.inWaiting()>0:
            byte = m.ser.read()
            m.c.update(byte)
            if not m.init_done and byte[0]==128:
                m.c[4].go_to(23,205)
                m.init_done = True
            
        if m.c[7].button==1:
            m.c[7].set_color((254,0,0))
            old_pos = mouse.getpos()
            new_pos = (old_pos[0],(old_pos[1]+5))
            mouse.move(new_pos[0],new_pos[1])
            
        if m.c[1].button==1:
            m.c[1].set_color((254,0,0))
            old_pos = mouse.getpos()
            new_pos = (old_pos[0],(old_pos[1]-5))
            mouse.move(new_pos[0],new_pos[1])
            
        if m.c[3].button==1:
            m.c[3].set_color((254,0,0))
            old_pos = mouse.getpos()
            new_pos = (old_pos[0]-5,(old_pos[1]))
            mouse.move(new_pos[0],new_pos[1])

        if m.c[5].button==1:
            m.c[5].set_color((254,0,0))
            old_pos = mouse.getpos()
            new_pos = (old_pos[0]+5,(old_pos[1]))
            mouse.move(new_pos[0],new_pos[1])
            
        if m.c[6].press_seconds()>4 and m.c[8].press_seconds()>4:
            shutdown()
            break

    sleep(0.01)
    

if __name__ == "__main__":
    main()