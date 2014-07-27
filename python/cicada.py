"""This module contains framework classes and methods for the Project CiCADA 3D interactive display"""

from datetime import datetime

class Cicada(object):
    """Stores the state of the CiCADA display and provides methods to manipulate it"""

    def num_pins = 9
    def led_per_pin = 4

    def __init__(self,serial):
        """Initialize display object connected to serial port"""
        self.serial = serial
        for n in range(self.num_pins):
            self.pin[n] = Pin(n,self.led_per_pin,serial)


    def set_all_colors(self,color):
        """Helper function to set all pins to the same color"""
        for n in range(self.num_pins):
            self.pin[n].set_color(color)


    def set_all_positions(self,position,speed):
        """Send all pins to 'position' at 'speed'"""
        for n in range(self.num_pins):
            self.pin[n].go_to(position,speed)

    
    def tare(self):
        """Tare the display heights"""
        self.serial.write(bytes([3,255]))


    def update(self,signal):
        """Call this when you have a serial event.  The cicada module does not read from serial."""
        if type(signal) == bytes:
            signal = signal[0]
        # TODO: convert signal (a binary string) to a number.
        for n in range(self.num_pins):
            self.pin[n].update(signal)


    def __getitem__(self,key):
        """Map index function to pins"""
        if type(key) != int:
            raise TypeError("Key should be an integer index")
        elif not (0 <= key < self.num_pins):
            raise IndexError("Key must be between 0 and %d exclusive"%self.num_pins)
        else:
            return self.pin[key]


    def __iter(self):
        return iter(self.pin)


    def keys(self):
        """For iterator support"""
        return range(self.num_pins)


class Pin(object):
    """Represents one pin of a CiCADA display"""

    def num = 0
    def serial = None

    def position = 0
    def speed = 0
    def button = 1

    def press_time = None
    def last_elapsed = 0

    def num_leds = 0
    def led = []


    def __init__(self,num,leds,serial):
        """Initialize a pin with a specified index and number of leds"""
        self.num = num
        self.num_leds = leds
        self.serial = serial
        for n in range(leds):
            led[n] = (0,0,0)


    def update(self,signal):
        """Update internal state in response to serial signal"""
        if self.num == signal:
            self._button_press(0)
        elif (255-self.num) == signal:
            self._button_press(1)


    def set_color(self,colors):
        """Sets the led colors of the pin. The colors should be a tuple or list of tuples.
        If the list is shorter than the number of LEDs, the sequence will repeat until all
        LEDs have been assigned a new color.  If the sequence is too long, it will be truncated."""
        colors = self._valid_color(colors)
        length = len(colors)
        for n in range(self.num_leds):
            color = self._valid_color_tuple(colors[n%length])
            serial.write(bytes([0,(self.num*self.num_leds+n),color[0],color[1],color[2],255]))
            self.led[n] = color


    def go_to(self,position,speed):
        """Move the pin to new 'position' at 'speed'"""
        self.position = position
        self.speed = speed
        cmd = 1 if self.position >= 0 else 2
        serial.write(bytes([cmd,self.num,position,speed,255]))

    def press_seconds(self):
        """Get the number of seconds the button has been pressed down for.
        If the button is currently not pressed, return 0"""
        if 0 == self.button:
            return 0
        else
            return datetime.now()-self.press_time


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
            if (0,0,0) <= color < (255,255,255):
                return color
            else:
                c2 = list(color)
                for i in range(3):
                    c2[i] = max(0,min(color[i],254))
                return tuple(c2)
        else:
            return (0,0,0)

     def _button_press(self,newstate):
         """Updates self in response to a button state change"""
         if 0 == newstate:
            press_time = datetime.now()
        else:
            last_elapsed = (press_time-datetime.now()).seconds
            press_time = None
        self.button = newstate
        # _fire_event('button',self.num,newstate)
               
