import cicada
import serial
from time import sleep
from datetime import datetime

class Jog(object):

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
        print("Event %d %d" %(index,state))
        print("Last elapsed %f"%self.c[index].last_elapsed)
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
                self.dt = datetime.now()
                # for i in range(9):
                    # self.c[i].go_to(self.c[index].position-2,205)
                for i in range(5):
                    self.c[i].go_to(self.c[index].position+2,205)
                sleep(2)
                for i in range(5,9):
                    self.c[i].go_to(self.c[index].position,205)
            elif self.armed_all_down:
                self.dt = datetime.now()
                # for i in range(9):
                    # self.c[i].go_to(self.c[index].position-2,205)
                for i in range(5):
                    self.c[i].go_to(self.c[index].position-2,205)
                sleep(2)
                for i in range(5,9):
                    self.c[i].go_to(self.c[index].position,205)            
def main():
    j = Jog()

    jog_i = -1
    j.dt = None
    
    try:
        while True:
            if j.ser.inWaiting()>0:
                byte = j.ser.read()
                if 0<=byte[0]<9:
                    if jog_i >=0 and jog_i != byte[0]:
                        j.c[jog_i].set_color((254,254,254))
                        jog_i = -1
                        j.armed_up = False
                        j.armed_down = False
                    else:
                        jog_i = byte[0]
                j.c.update(byte)
            
            if 1<j.c[jog_i].press_seconds()<4 and not (j.armed_up or j.armed_down or j.armed_all_up or j.armed_all_down):
                j.c[jog_i].set_color((0,0,254))
                j.armed_up = True
                j.dt = datetime.now()
                
            if j.armed_up and j.c[jog_i].press_seconds()>1 and ((datetime.now()-j.dt).seconds)>1:
                j.c[jog_i].set_color((254,254,0))
                j.armed_up = False
                j.armed_down = True
                j.dt = datetime.now()
                
            if j.dt is not None and ((datetime.now()-j.dt).seconds)>6:
                j.c[jog_i].set_color((254,254,254))
                j.armed_up = False
                j.armed_down = False
                j.armed_all_up = False
                j.armed_all_down = False
                j.dt = None
                jog_i = -1
                
            if j.armed_down and j.c[jog_i].press_seconds()>1 and ((datetime.now()-j.dt).seconds)>1:
                if jog_i == 4: 
                    j.c[jog_i].set_color((0,254,0))
                    j.armed_down = False
                    j.armed_all_up = True
                    j.dt = datetime.now()

            if j.armed_all_up and j.c[jog_i].press_seconds()>1 and ((datetime.now()-j.dt).seconds)>1:
                if jog_i == 4: 
                    j.c[jog_i].set_color((254,0,0))
                    j.armed_all_up = False
                    j.armed_all_down = True
                    j.dt = datetime.now()                    

    finally:
        j.ser.close()
        
if __name__ == "__main__":
    main()