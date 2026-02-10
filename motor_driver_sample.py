from machine import Pin, PWM
import time


# === 2A DUAL MOTOR CONTROLLER ===
# Motor Pins
E1 = PWM(Pin(0))  # Left motor PWM
M1 = Pin(1, Pin.OUT)
E2 = PWM(Pin(3))  # Right motor PWM
M2 = Pin(4, Pin.OUT)

# Motor Frequencies
E1.freq(500)
E2.freq(500)

# Function to control motor speed
def motor_control(E, M, direction = "stop", speed = 0):
    if direction == "forward":
        M.value(1)
        E.duty_u16(speed)
    elif direction == "backward":
        M.value(0)
        E.duty_u16(speed)
    else:
        E.duty_u16(speed)


while True:
    # Testing left motor
    motor_control(E1, M1, "forward", 40000)
    time.sleep(2)
    motor_control(E1, M1, "backward", 40000)
    time.sleep(2)
    motor_control(E1, M1, "stop", 0)
    time.sleep(1)

    # Testing right motor
    motor_control(E2, M2, "forward", 40000)
    time.sleep(2)
    motor_control(E2, M2, "backward", 40000)
    time.sleep(2)
    motor_control(E2, M2, "stop", 0)
    time.sleep(1)

    # Testing both motors
    motor_control(E1, M1, "forward", 40000)
    motor_control(E2, M2, "forward", 40000)
    time.sleep(2)
    motor_control(E1, M1, "backward", 40000)
    motor_control(E2, M2, "backward", 40000)
    time.sleep(2)
    motor_control(E1, M1, "stop", 0)
    motor_control(E2, M2, "stop", 0)
    time.sleep(1)
    


