import numpy
import pyaudio
import math
from datetime import datetime
import serial
import cicada

# Initiate serial and cicada
ser = serial.Serial('COM3', 9600)
c = cicada.Cicada(ser)

# Initialize PyAudio
pyaud = pyaudio.PyAudio()

# Open input stream, 16-bit mono at 44100 Hz
# On my system, device 2 is a USB microphone, your number may differ.
stream = pyaud.open(
    format = pyaudio.paInt16,
    channels = 1,
    rate = 44100,
    input_device_index = 0,
    input = True)
    
# Define variables
prev_loudness = 0
lambda_ = 0.5
snake = [0,1,2,5,8,7,6,3]
snake_num_up = 0
snake_num_down = 4
dt = datetime.now()
sustain = True

while True:

# Read raw microphone data
    rawsamps = stream.read(1024)
    
# Convert raw data to NumPy array
    samps = numpy.fromstring(rawsamps, dtype=numpy.int16)
    data = numpy.array(samps, dtype=float) / 32768.0
    ms = math.sqrt(numpy.sum(data ** 2.0) / len(data))
    if ms < 10e-8: ms = 10e-8
    loudness_raw = 10.0 * math.log(ms, 10.0)
    loudness = ((prev_loudness * lambda_) + loudness_raw * (1 - lambda_))
       
# Set loudness delta to trigger sustained white LED flash for n voxels
    if (loudness - prev_loudness) > 2 and not sustain:
        print('sustain on')
        c.random_sustain(3)
        sustain = True
    
# Set loudness delta to end sustained white LED flash for n voxels
    if (loudness - prev_loudness) < -1 and sustain:
        c.clear_sustain()
        sustain = False
        print('sustain off')

    prev_loudness = loudness

# Define snaking motion in display
    if ((datetime.now() - dt).seconds) == 1:
        dt = datetime.now()
        c[snake[snake_num_up]].go_to(3,205)
        c[snake[snake_num_down]].go_to(0,205)
        snake_num_up += 1
        snake_num_down += 1
        if snake_num_up == 8:
            snake_num_up = 0
        if snake_num_down == 8:
            snake_num_down = 0

