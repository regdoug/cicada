import cicada
import serial
from time import sleep
from datetime import datetime

class Background(object):

    wait = False
    init_done = False
    armed = False
    green = False
    armed_up = False
    armed_down = False
    armed_all_up = False
    armed_all_down = False
    
    def __init__(self):
        self.ser = serial.Serial('COM3', 9600)
        self.c = cicada.Cicada(self.ser)
        self.dt = datetime.now()
        self.c.add_observer(self.event)

    def event(self,type,index,state):
        if not self.init_done:
            if index == 8 and state == 0:
                for i in range(9):
                    self.c[i].set_color((254,254,254))
        if self.armed and state == 1:
            if index == 4:
                self.c.tare()
                self.c[4].set_color((0,254,0))
                self.dt = datetime.now()
                self.green = True
            self.armed = False
        if state == 1:
            self.dt = datetime.now()
        if state == 0 and self.c[index].last_elapsed<1:
            if self.armed_up:
                self.dt = datetime.now()
                self.c[index].go_to(self.c[index].position+2,205)
            elif self.armed_down:
                self.dt = datetime.now()
                self.c[index].go_to(self.c[index].position-2,205)
            elif self.armed_all_up:
                self.wait = True
                self.dt = datetime.now()
                # for i in range(9):
                    # self.c[i].go_to(self.c[index].position-2,205)
                for i in range(5):
                    self.c[i].go_to(self.c[index].position+2,205)
                sleep(2)
                for i in range(5,9):
                    self.c[i].go_to(self.c[index].position,205)
                sleep(2)
                self.wait = False
            elif self.armed_all_down:
                self.wait = True
                self.dt = datetime.now()
                # for i in range(9):
                    # self.c[i].go_to(self.c[index].position-2,205)
                for i in range(5):
                    self.c[i].go_to(self.c[index].position-2,205)
                sleep(2)
                for i in range(5,9):
                    self.c[i].go_to(self.c[index].position,205)   
                sleep(2)
                self.wait = False
def main():
    b = Background()

    jog_i = -1
    b.dt = None
    
    def shutdown():
        for i in range(9):
            b.c[i].go_to(0,205)
            sleep(0.1)
    
    try:
        while True:
            if b.ser.inWaiting()>0 and not b.wait:
                byte = b.ser.read()
                if 0<=byte[0]<9:
                    if jog_i >=0 and jog_i != byte[0]:
                        b.c[jog_i].set_color((254,254,254))
                        jog_i = -1
                        b.armed_up = False
                        b.armed_down = False
                    else:
                        jog_i = byte[0]
                b.c.update(byte)
            
            if 1<b.c[jog_i].press_seconds()<4 and not (b.armed_up or b.armed_down or b.armed_all_up or b.armed_all_down):
                b.c[jog_i].set_color((0,0,254))
                b.armed_up = True
                b.dt = datetime.now()
                
            if b.armed_up and b.c[jog_i].press_seconds()>1 and ((datetime.now()-b.dt).seconds)>1:
                b.c[jog_i].set_color((254,254,0))
                b.armed_up = False
                b.armed_down = True
                b.dt = datetime.now()
                
            if b.dt is not None and ((datetime.now()-b.dt).seconds)>4:
                b.c[jog_i].set_color((254,254,254))
                b.armed_up = False
                b.armed_down = False
                b.armed_all_up = False
                b.armed_all_down = False
                b.armed = False
                b.dt = None
                jog_i = -1
                
            if b.armed_down and b.c[jog_i].press_seconds()>1 and ((datetime.now()-b.dt).seconds)>1:
                if jog_i == 4: 
                    b.c[jog_i].set_color((0,254,254))
                    b.armed_down = False
                    b.armed_all_up = True
                    b.dt = datetime.now()

            if b.armed_all_up and b.c[jog_i].press_seconds()>1 and ((datetime.now()-b.dt).seconds)>1:
                if jog_i == 4: 
                    b.c[jog_i].set_color((254,1,0))
                    b.armed_all_up = False
                    b.armed_all_down = True
                    b.dt = datetime.now()    

            if b.c[4].press_seconds()>9:
                b.c[4].set_color((254,0,0))
                b.armed = True
                b.armed_up = False
                b.armed_down = False
                b.armed_all_down = False
                b.armed_all_up = False
                b.dt = datetime.now()
                
            if b.green and b.dt is not None and ((datetime.now()-b.dt).seconds)>4:
                b.c[4].set_color((254,254,254))
                b.green = False
                b.dt = None
                
            if b.armed and b.dt is not None and ((datetime.now()-b.dt).seconds)>4:
                b.armed = False
                b.c.set_all_colors((254,254,254))
                b.dt = None         

            if b.c[6].press_seconds()>4 and b.c[8].press_seconds()>4:
                shutdown()
                break                

    finally:
        b.ser.close()
        
if __name__ == "__main__":
    main()