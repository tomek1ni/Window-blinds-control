#!/usr/bin/python
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import time
import threading
import serial
import socket
import board
import busio
import adafruit_ads1x15.ads1015 as ADS
import schedule
from adafruit_ads1x15.analog_in import AnalogIn
from bluedot import BlueDot

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BCM) #

#time.sleep(10)
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1015(i2c)
chan = AnalogIn(ads, ADS.P0)
ads.gain = 2
stop = False
failSafe = False

UDP_IP = "192.168.0.30"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

BUTT_L = 18
BUTT_R = 23
DIR = 17
STEP = 27
SLEEP = 22
arr = ['b', 's']
leftState = False
rightState = False
timeState = False
bd = BlueDot(cols=2, rows=2)
bd[0, 1].color = "green"
bd[1, 1].color = "red"

GPIO.setup(BUTT_L, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Button L.
GPIO.setup(BUTT_R, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Button P.
GPIO.setup(DIR, GPIO.OUT, initial=GPIO.LOW) # Directon 
GPIO.setup(STEP, GPIO.OUT, initial=GPIO.LOW) # Step
GPIO.setup(SLEEP, GPIO.OUT, initial=GPIO.LOW) # Sleep

def fun_udp():
    while True:
        global arr
        try:                                    # https://www.programmersought.com/article/708917122/
            sock.settimeout(0.15)               # Setting time out period for when data is not received (remote button not pressed)
            data, addr = sock.recvfrom(1024)    # buffer size is 1024 bytes
            arr = str(data).split()
        except socket.timeout:      # In case of open/close command not coming from remote machine through UDP
            arr[1] = 's'            # assign 's' to arr to prevent it from getting stuck opening or closing

def fun_butts():
    while True:
        global leftState
        global rightState
        if (GPIO.input(BUTT_L) == True or bd[0,0].is_pressed == True) and rightState == False:
            leftState = True
        else:
            leftState = False
        if (GPIO.input(BUTT_R) == True or bd[1,0].is_pressed == True) and leftState == False:
            rightState = True
        else:
            rightState = False
        time.sleep(0.1)

def Steps():
    GPIO.output(STEP,1)
    time.sleep(0.0005)
    GPIO.output(STEP,0)
    time.sleep(0.0005)

def average  ():
    global array
    tempArray = array [:9]
    for j in range (9,0,-1):
        array[j] = tempArray[j-1]
    array[0] = chan.value
    aver = sum (array)/len(array)
#    print ("prevAver :", prevAver ,", aver :", aver)
    return(aver)

def reset_aver ():
    global array
    global aver
    global prevAver
    array = [30000,30000,30000,30000,30000,30000,30000,30000,30000,30000]
    prevAver = 30010
    aver = 30000

def close_blinds():
    global prevAver
    global aver
    n = 0
    global failSafe
    GPIO.output(SLEEP,1)
    GPIO.output(DIR,0)
    while (prevAver > aver or aver > 22000) and failSafe == False :
        prevAver = aver
        aver = average ()
        GPIO.output(STEP,1)
        time.sleep(0.0005)
        GPIO.output(STEP,0)       
        n += 1
        if n > 3000 :
            failSafe = True 
#        print ("prevAver :", prevAver ,", aver :", aver, ", n:", n)
    reset_aver()
    GPIO.output(SLEEP,0)

def open_blinds ():
    if failSafe == False:
        close_blinds()
        GPIO.output(SLEEP,1)
        GPIO.output(DIR,1)
        for i in range (2200):
            Steps()
        GPIO.output(SLEEP,0)  

schedule.every().day.at("21:00:00").do(close_blinds)
schedule.every().day.at("06:05:00").do(open_blinds)

reset_aver()

udp = threading.Thread(target=fun_udp)
udp.start()
butts = threading.Thread(target=fun_butts)
butts.start()

while True:
    schedule.run_pending()

    if arr[1] == 'l' or (leftState == True and rightState == False):
        GPIO.output(SLEEP,1)
        GPIO.output(DIR,1)
        while arr[1] == 'l' or (leftState == True and rightState == False):
            Steps()

    elif arr[1] == 'r' or (leftState == False and rightState == True):
        GPIO.output(SLEEP,1)
        GPIO.output(DIR,0)
        while arr[1] == 'r' or (leftState == False and rightState == True):
            Steps()

    elif bd[0,1].is_pressed == True:
        open_blinds()

    elif bd[1,1].is_pressed == True:
        close_blinds()

    elif arr[1] == 's' or (leftState == False and rightState == False) or timeState == False:
        GPIO.output(SLEEP,0)

    else :
        GPIO.output(SLEEP,0)