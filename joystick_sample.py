from machine import ADC, Pin
import time

# =====================
# HARDWARE SETUP
# =====================
adc_x = ADC(27)			# Joystick horizontal (x-axis)
adc_y = ADC(26)			# Joystick vertical (y-axis)
sw = Pin(22, Pin.IN, Pin.PULL_UP)	# Joystick button

# =====================
# TEST JOYSTICK
# =====================
def test_joystick():
    # Get data from joystick
    x_val = adc_x.read_u16()
    y_val = adc_y.read_u16()
    sw_val = sw.value()
    
    # Set default position to "middle"
    x_dir, y_dir = "middle", "middle"
    
    # Check for position change on x-axis
    if x_val < 20000:
        x_dir = "left"  
    elif x_val > 50000:
        x_dir = "right"  
        
    # Check for position change on y-axis
    if y_val < 20000:
        y_dir = "up"
    elif y_val > 50000:
        y_dir = "down"

    # Check button status
    if sw_val == 0:
        print("PRESS")
        
    print(f"{x_dir}, {y_dir}")
    
    time.sleep(1)

while True:
    test_joystick()


