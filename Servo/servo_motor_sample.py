from machine import Pin
from time import sleep
from servo import Servo # Save this file on pico

# =========================
# HARDWARE SETUP
# =========================
sg90 = Servo(Pin(22))

# =========================
# TESTING SERVO
# =========================
while True:
    sg90.move(0) # move to 0 degree postion
    sleep(2)
    
    sg90.move(90) # move to 90 degree position
    sleep(2)
    
    sg90.move(180) # move to 180 degree position
    sleep(2)
    
    sg90.move(90) # move to 90 degree position
    sleep(2)