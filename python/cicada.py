"""This module contains framework classes and methods for the Project CiCADA 3D interactive display"""

from datetime import datetime
from time import sleep
import random as r

class Cicada(object):
    """Stores the state of the CiCADA display and provides methods to manipulate it"""

    num_Voxels = 9
    led_per_Voxel = 4
    num_leds = num_Voxels*led_per_Voxel
    
    Voxel = []
    idx = []

    def __init__(self,serial):
        """Initialize display object connected to serial port"""
        self.serial = serial
        for n in range(self.num_Voxels):
            self.Voxel.append( Voxel(n,self.led_per_Voxel,serial) )


    def set_all_colors(self,color):
        """Helper function to set all Voxels to the same color"""
        for Voxel in self.Voxel:
            Voxel.set_color(color)


    def set_all_positions(self,position,speed):
        """Send all Voxels to 'position' at 'speed'"""
        for Voxel in self.Voxel:
            Voxel.go_to(position,speed)
    
    def tare(self):
        """Tare the display heights"""
        self.serial.write(bytes([3,255]))
        
            
    def randomize_colors(self,num_Voxels):
        """Give random colors to all leds"""
        idx = list(range(self.num_Voxels))
        r.shuffle(idx)
        idx = idx[:num_Voxels]
        for i in idx:
            print(i)
            colors = []
            for n in range(self.num_leds):
                colors.append((r.randint(0,1)*254,r.randint(0,1)*254,r.randint(0,1)*254))
            self[i].set_color(colors)
            self[i].set_color((0,0,0))
            
            
    def random_flash(self,num_Voxels):
        """Give random colors to all leds"""
        idx = list(range(self.num_Voxels))
        r.shuffle(idx)
        idx = idx[:num_Voxels]
        for i in idx:
            self[i].set_color((254,254,254))
            self[i].set_color((0,0,0))

            
    def random_sustain(self,num_Voxels):
        """Give random colors to all leds"""
        self.idx = []
        idx = list(range(self.num_Voxels))
        r.shuffle(idx)
        idx = idx[:num_Voxels]
        for i in idx:
            self.idx.append(i)
            self[i].set_color((254,254,254))
            
            
    def clear_sustain(self):
        """Give random colors to all leds"""
        print(self.idx)
        for i in self.idx:
            self[i].set_color((0,0,0))
            

    def update(self,signal):
        """Call this when you have a serial event.  The cicada module does not read from serial."""
        if type(signal) == bytes:
            signal = signal[0]
        for Voxel in self.Voxel:
            Voxel.update(signal)


    def add_observer(self,observer):
        self.Voxel[0].add_observer(observer)


    def __getitem__(self,key):
        """Map index function to Voxels"""
        if type(key) != int:
            raise TypeError("Key should be an integer index")
        elif not (-1 <= key < self.num_Voxels):
            raise IndexError("Key must be between 0 and %d exclusive"%self.num_Voxels)
        else:
            return self.Voxel[key]


    def __iter(self):
        return iter(self.Voxel)


    def keys(self):
        """For iterator support"""
        return range(self.num_Voxels)


class Voxel(object):
    """Represents one Voxel of a CiCADA display"""

    num = 0
    serial = None

    position = 0
    speed = 0
    button = 0

    press_time = None
    last_elapsed = 0

    num_leds = 0
    led = []

    _observers = []


    def __init__(self,num,leds,serial):
        """Initialize a Voxel with a specified index and number of leds"""
        self.num = num
        self.num_leds = leds
        self.serial = serial
        for n in range(leds):
            self.led.append((0,0,0))


    def update(self,signal):
        """Update internal state in response to serial signal"""
        if self.num == signal:
            self._button_press(1)
        elif (255-self.num) == signal:
            self._button_press(0)


    def set_color(self,colors):
        """Sets the led colors of the Voxel. The colors should be a tuple or list of tuples.
        If the list is shorter than the number of LEDs, the sequence will repeat until all
        LEDs have been assigned a new color.  If the sequence is too long, it will be truncated."""
        colors = self._valid_color(colors)
        length = len(colors)
        for n in range(self.num_leds):
            color = self._valid_color_tuple(colors[n%length])
            self.serial.write(bytes([0,(self.num*self.num_leds+n),int(color[0]),int(color[1]),int(color[2]),255]))
            self.led[n] = color


    def go_to(self,position,speed):
        """Move the Voxel to new 'position' at 'speed'"""
        print(self.num,self.position,self.speed)
        self.position = position
        self.speed = speed
        cmd = 1 if self.position >= 0 else 2
        self.serial.write(bytes([cmd,self.num,abs(position),speed,255]))
        
        
    def press_seconds(self):
        """Get the number of seconds the button has been pressed down for.
        If the button is currently not pressed, return 0"""
        if 0 == self.button or self.press_time is None:
            return 0
        else:
            return (datetime.now()-self.press_time).seconds

    def add_observer(self,observer):
        self._observers.append(observer)

    def _valid_color(self,color):
        """Takes the provided color or list of colors and returns a valid list of colors"""
        if isinstance(color, tuple):
            return [self._valid_color_tuple(color)]
        elif isinstance(color, list):
            return [self._valid_color_tuple(c) for c in color]
        else:
            return [(0,0,0)]

    def _valid_color_tuple(self,color):
        """Takes the provided color (hopefully a 3-element tuple) and converts it to a valid color"""
        if len(color) == 3:
            if (0,0,0) <= color <= (256,256,256):
                return color
            else:
                c2 = list(color)
                for i in range(3):
                    c2[i] = max(0,min(color[i],256))
                return tuple(c2)
        else:
            return (0,0,0)

    def _button_press(self,newstate):
        """Updates self in response to a button state change"""
        print("Voxel %d newstate %d"%(self.num,newstate))
        if 1 == newstate:
            self.press_time = datetime.now()
        else:
            if self.press_time is not None:
                self.last_elapsed = (datetime.now()-self.press_time).seconds
            else:
                self.last_elapsed = 0
            self.press_time = None
        self.button = newstate
        self._fire_event('button',self.num,newstate)

    def _fire_event(self,type,index,state):
        for observer in self._observers:
            observer(type,index,state)
