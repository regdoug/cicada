import cicada
import serial
from time import sleep
import numpy as np
import csv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class Grapher(FileSystemEventHandler):

# Define color strings as RGB color data
    colors = {
        'red':(254,0,0),
        'green':(0,254,0),
        'blue':(0,0,254),
        'yellow':(254,254,0),
        'purple':(254,0,254),
        'cyan':(0,254,254),
        'white':(254,254,254),
        'orange':(254,1,0),
        'gray':(200,200,200),
    }

# Initiate serial and cicada
    def __init__(self):
        self.ser = serial.Serial('COM3', 9600)
        self.c = cicada.Cicada(self.ser)

# Define event to occur when grapher.csv is modified
# Translate excel y-values to numbers in stepper range
# Go to position and set color for pins defined in .csv file
    def on_modified(self,event):
        if 'grapher.csv' in event.src_path:
            with open('grapher.csv') as csvfile:
                spamreader = csv.reader(csvfile)
                data = []
                for row in spamreader:
                    if len(row) >= 3:
                        data.append( [int(row[0]), float(row[1]), row[2]] )
                max_pos = 1
                min_pos = 0
                for row in data:
                    if row[1] > max_pos:
                        max_pos = row[1]
                    elif row[1] < min_pos:
                        min_pos = row[1]
                for row in data:
                    pos = ((33/(max_pos-min_pos))*(row[1]-min_pos))
                    if row[2] in self.colors.keys():
                        color = self.colors[row[2]]
                    else:
                        color = (0, 0, 0)
                    self.c[int(row[0])].go_to(int(pos),205)
                    self.c[int(row[0])].set_color(color)

# Define event handler, observer, sleep                    
if __name__ == "__main__":
    event_handler = Grapher()
    observer = Observer()
    observer.schedule(event_handler, '.')
    observer.start()
    try:
        while True:
            sleep(5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()







          
        