import cicada
import serial
from time import sleep
from pyxll import xl_func
from multiprocessing.connection import Client
import numpy as np

address = ('localhost', 6000)    
listener = Listener(address, authkey='secret password')
conn = listener.accept()
print 'connection accepted from', listener.last_accepted
data = []
while True:
    msg = conn.recv()
    if msg == 'close':
        conn.close()
        break
    else:    
        data.append(msg)

listener.close()

data = np.array(data)
max_pos = np.max(data[:,1])
min_pos = np.min(0,np.min(data[:,1]))

data[:,1] = ((33/(max_pos-min_pos))*(data[:,1]-min_pos))

for row in data:
    c[row[0]].go_to(row[1],205)
    if row[2] == 'red':
        color = (254,0,0)
    elif row[2] == 'green':
        color = (0, 254, 0)
    elif row[2] == 'blue':
        color = (0, 0, 254)
    elif row[2] == 'yellow':
        color = (254, 254, 0)
    elif row[2] == 'purple':
        color = (254, 0, 254)
    elif row[2] == 'cyan':
        color = (0, 254, 254)
    elif row[2] == 'white':
        color = (254, 254, 254)
    elif row[2] == 'orange':
        color = (254, 128, 0)
    else:
        color = (0, 0, 0)
    c[row[2]].set_color(color)