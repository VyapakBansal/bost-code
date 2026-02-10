from machine import Pin
import time

# =====================
# HARDWARE SETUP
# =====================
button = Pin(13, Pin.IN, Pin.PULL_UP)

# =====================
# TEST BUTTON
# =====================
def test_button():
    # Get button state
    button_val = button.value()  
    
    # Check button state
    if button_val:
        print("WAITING...")    
    else:
        print("PRESS")
        
    time.sleep(1)

while True:
    test_button()
