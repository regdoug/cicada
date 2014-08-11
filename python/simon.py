import cicada
import serial
from time import sleep
from datetime import datetime
import random as r
import winsound
import numpy


class Simon(object):

# Define variables and player and simon arrays, initiate datetime
# Define display colors and beep frequency
    new_game = True
    red = False
    inprogress = False
    dt = datetime.now()
    press_number = 0
    simon = []
    colors = [(0,0,254),(254,254,0),(0,254,0),(254,0,0),(254,254,254),(254,0,0),(0,254,0),(254,254,0),(0,0,254)]
    beep_frequency = [200, 250, 300, 375, 450, 550, 650, 850, 1050]
    player = []
    
# Initiate serial, cicada, datetime, observer
    def __init__(self):
        self.ser = serial.Serial('COM3', 9600)
        self.c = cicada.Cicada(self.ser)
        self.dt = datetime.now()
        self.c.add_observer(self.event)
        
# Define add on to add new button to simon sequence
    def add_on(self):
        print("adding on to simon")
        i = r.randint(0,8)
        self.dt = datetime.now()
        self.simon.append(i)
        self.player.clear()
        self.press_number = -1
    
# Define display to display simon sequence colors and sounds
    def display(self):
        print("display")
        print(self.simon)
        sleep(0.5)
        for pin in self.simon:
            self.c[pin].set_color(self.colors[pin])
            winsound.Beep(self.beep_frequency[pin],500)
            self.dt = datetime.now()
            self.c[pin].set_color((0,0,0))
            sleep(0.15)
            while self.ser.inWaiting()>0:
                self.ser.read()
            
# Define losing display, reset variables
    def lose(self):
        print("lose")
        self.c.set_all_colors((254,0,0))
        winsound.Beep(200,2000)
        self.dt = datetime.now()
        self.simon.clear()
        self.player.clear()
        self.press_number = -1
        self.new_game = False
        self.inprogress = False
        self.red = True
        
# Define initial display and initiate event
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
                # Define initial display
                self.c.set_all_colors((254,254,254))
                self.c[4].set_color((0,254,0))
        elif self.inprogress:
            print("inprogress")
            if state == 1:
                # Record player presses and display colors and sounds
                self.press_number += 1
                self.dt = datetime.now()
                self.player.append(index)
                if self.simon[self.press_number] == self.player[self.press_number]:
                    self.c[index].set_color(self.colors[index])
                    winsound.Beep(self.beep_frequency[index],500)
                if self.simon[self.press_number] != self.player[self.press_number]:
                    self.lose()
            else:
                # Add on if arrays are equal
                self.c[index].set_color((0,0,0))
                if self.press_number == len(self.simon)-1:
                    self.add_on()
                    self.display()
            

def main():

    s = Simon()
    press_number = 0
    
# Define shutdown process
    def shutdown():
        for i in range(9):
            s.c[i].go_to(0,205)
            sleep(15)
    
    try:
        while True:
# Initialize serial reading
            if s.ser.inWaiting()>0:
                byte = s.ser.read()
                s.c.update(byte)
                
# Reset to be ready for new game after loss
            if s.red and ((datetime.now()-s.dt).seconds)>2:
                s.c.set_all_colors((254,254,254))
                s.c[4].set_color((0,254,0))
                s.red = False
                s.new_game = True
                                
# Define lose if wait more than 3 seconds to push button
            if ((datetime.now()-s.dt).seconds)>2 and not s.new_game:
                print("You took too long!")
                s.lose()
             
# Define shutdown as holding buttons 6 and 8 for 5 seconds             
            if s.c[6].press_seconds()>4 and s.c[8].press_seconds()>4:
                shutdown()
                break
                        
            sleep(0.01)
    finally:
        s.ser.close()
        
if __name__ == "__main__":
    main()