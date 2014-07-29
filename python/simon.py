import cicada
import serial
from time import sleep
from datetime import datetime
import random as r


class Simon(object):

    new_game = True
    red = False
    inprogress = False
    dt = datetime.now()
    press_number = 0
    simon = []
    colors = [(0,0,254),(254,254,0),(0,254,0),(254,0,0),(254,254,254),(254,0,0),(0,254,0),(254,254,0),(0,0,254)]
    player = []
    
    def __init__(self):
        self.ser = serial.Serial('COM3', 9600)
        self.c = cicada.Cicada(self.ser)
        self.dt = datetime.now()
        self.c.add_observer(self.event)
        
    def add_on(self):
        print("adding on to simon")
        i = r.randint(0,7)
        self.dt = datetime.now()
        self.simon.append(i)
        self.player.clear()
        self.press_number = -1
    
        
    def display(self):
        print("display")
        print(self.simon)
        sleep(0.5)
        for pin in self.simon:
            self.c[pin].set_color(self.colors[pin])
            sleep(0.5)
            self.dt = datetime.now()
            self.c[pin].set_color((0,0,0))
            sleep(0.15)
            
    def lose(self):
        print("lose")
        self.c.set_all_colors((254,0,0))
        self.dt = datetime.now()
        self.simon.clear()
        self.player.clear()
        self.press_number = -1
        self.new_game = False
        self.inprogress = False
        self.red = True
        

    def event(self,type,index,state):
        print("Event %d %d" %(index,state))
        if self.new_game:
            print("new game")
            if index == 4 and state == 1:
                self.c.set_all_colors((0,0,0))
                self.new_game = False
                self.inprogress = True
                self.add_on()
                self.display()
            if index == 8 and state == 0:
                #Hack to make sure white and green show for first game
                self.c.set_all_colors((254,254,254))
                self.c[4].set_color((0,254,0))
        elif self.inprogress:
            print("inprogress")
            if state == 1:
                #Record player presses
                self.press_number += 1
                self.dt = datetime.now()
                self.player.append(index)
                if self.simon[self.press_number] == self.player[self.press_number]:
                    self.c[index].set_color(self.colors[index])
                if self.simon[self.press_number] != self.player[self.press_number]:
                    self.lose()
            else:
                self.c[index].set_color((0,0,0))
                if self.press_number == len(self.simon)-1:
                    self.add_on()
                    self.display()
            

def main():
    s = Simon()
    press_number = 0
    
    try:
        while True:
            if s.ser.inWaiting()>0:
                byte = s.ser.read()
                s.c.update(byte)
                
            if s.red and ((datetime.now()-s.dt).seconds)>2:
                s.c.set_all_colors((254,254,254))
                s.c[4].set_color((0,254,0))
                s.red = False
                s.new_game = True
                            
                if ((datetime.now()-s.dt).seconds)>2 and not s.new_game:
                    print("You took too long!")
                    s.lose()
                        
            sleep(0.01)
    finally:
        s.ser.close()
        
if __name__ == "__main__":
    main()