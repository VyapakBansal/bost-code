from machine import Pin
import time

# =====================
# HARDWARE SETUP
# =====================
button = Pin(13, Pin.IN, Pin.PULL_UP)
led = Pin('LED', Pin.OUT)
output = Pin(0, Pin.out)
# =====================
# TEST BUTTON
# =====================
def test_button():
    # Get button state
    button_val = button.value()  
    
    # Check button state
    if button_val:
        print("WAITING...")
        led.on()
        output.on()
        time.sleep(5)
        led.off()
        output()
        time.sleep(1)
    else:
        print("PRESS")
        
    time.sleep(1)

while True:
    test_button()
