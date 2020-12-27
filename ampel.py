#!/usr/bin/env python3
'''
use audio input to generate a VU-Meter like digital output.
some kind of auto-level is crudely implemented, to match the actual audio level

requires: pyaudio, numpy, RPi.GPIO

setup of /etc/asound.conf is necesarry
see https://www.alsa-project.org/wiki/Setting_the_default_device

GPIO11: green
GPIO13: orange
GPIO15: red

Thanks to Scott W Harden for his good documentation. 
https://swharden.com/blog/2016-07-19-realtime-audio-visualization-in-python/
'''

import pyaudio
import numpy as np

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges. \
         You can achieve this by using 'sudo' to run your script")

def main():
    initGPIO()

    maxValue = 2**16
    bars = 10
    #configure audio input first
    p=pyaudio.PyAudio()
    stream=p.open(format=pyaudio.paInt16,channels=1,rate=22050,
                input=True, frames_per_buffer=1048)

    buffersize = 20
    lastPeaks = [0] * buffersize
    i = buffersize #overflow in first run, so achtually start with 0

    try:
        while True:
            #get 1048 bytes, get max value afterwards
            data = np.fromstring(stream.read(1048),dtype=np.int16)
            tmp_peak = np.abs(np.max(data)-np.min(data))/maxValue
            i+=1
            if i >= buffersize:
                i=0
            lastPeaks[i] = tmp_peak
            #fourth = max(lastPeaks) /4
            #level = int((tmp_peak*1.25) / fourth)-1

            fourth = (sum(lastPeaks)/len(lastPeaks))/4
            #fourth = max(lastPeaks) /4
            level = int((tmp_peak) / fourth)-1

            #set led's according to calculated level
            setLED(level)
    except KeyboardInterrupt:
        pass


def initGPIO():
    ''' initalize and setup gpio-pins as outputs '''
    #setup gpio's
    # to use Raspberry Pi board pin numbers
    GPIO.setmode(GPIO.BOARD)

    #green - gpio11
    GPIO.setup(11, GPIO.OUT)
    GPIO.output(11, GPIO.LOW)

    #orange - gpio13
    GPIO.setup(13, GPIO.OUT)
    GPIO.output(13, GPIO.LOW)

    #red - gpio15
    GPIO.setup(15, GPIO.OUT)
    GPIO.output(15, GPIO.LOW)

def setLED(val):
    ''' turn on and off the led's '''
    if val == 1:
        #led green
        GPIO.output(11, GPIO.HIGH)#green
        GPIO.output(13, GPIO.LOW)#orange
        GPIO.output(15, GPIO.LOW)#red
        print ("#")
    elif val == 2:
        #led green & orange
        GPIO.output(11, GPIO.HIGH)#green
        GPIO.output(13, GPIO.HIGH)#orange
        GPIO.output(15, GPIO.LOW)#red
        print ("##")
    elif val == 3:
        #led green & orange & red 
        GPIO.output(11, GPIO.HIGH)#green
        GPIO.output(13, GPIO.HIGH)#orange
        GPIO.output(15, GPIO.HIGH)#red
        print ("###")
    else:
        #all leds off
        GPIO.output(11, GPIO.LOW)#green
        GPIO.output(13, GPIO.LOW)#orange
        GPIO.output(15, GPIO.LOW)#red

if __name__ == "__main__":
    main()
