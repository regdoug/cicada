from pyxll import xl_func
from multiprocessing.connection import Client
import numpy as np


@xl_func("float[] pin, float[] position, float[] color : float")
def cicada_grapher(pin,position,color):
    """takes arguments pin numbers, y-values, colors"""
    pin = np.array(pin)
    position = np.array(position)
    color = np.array(color)
    
    if pin.shape != position.shape or pin.shape != color.shape:
        return 1;
    
    address = ('localhost', 6000)
    conn = Client(address, authkey='secret password')
            
    for i in range(len(pin)):
        conn.send([pin[i],position[i],color[i]])
            
    conn.send('close')
    conn.close()

    return total