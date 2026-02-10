from machine import Pin
from time import sleep

# Set LED pin
led = Pin(2, Pin.OUT)

# Test LED
while True:
    led.on()
    sleep(1)
    led.off()
    sleep(1)

