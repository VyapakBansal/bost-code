import aioble
import bluetooth
import uasyncio as asyncio
from machine import Pin, PWM

# RENAME THIS FILE TO main.py WHEN SAVING TO THE PI PICO (Boat)

# ===============================
# RECEIVER CONFIG
# ===============================

_REMOTE_NAME = "engg_200"                               # Your group name, i.e 'B1_A1' for Block 1, Group A1
_GENERIC_SERVICE_UUID = bluetooth.UUID(0x1848)      
_JOYSTICK_CHARACTERISTIC_UUID = bluetooth.UUID(0x2A6E)

connected = False
led = Pin("LED", Pin.OUT)       # LED on Pi Pico
led_green = Pin(2, Pin.OUT)     # Make sure pin number matches wiring

# ===============================
# MOTOR PINS (L298N)
# ===============================

# Make sure pin numbers match wiring
E1 = PWM(Pin(0))  # Left motor PWM
M1 = Pin(1, Pin.OUT)
E2 = PWM(Pin(3))  # Right motor PWM
M2 = Pin(4, Pin.OUT)

# Set PWM frequencies
E1.freq(500)
E2.freq(500)

# ===============================
# DEADZONE & MAX SPEED
# ===============================

DEADZONE_LOW = -2
DEADZONE_HIGH = 2
MAX_SPEED = 100

# ===============================
# MOTOR CONTROL
# ===============================

def set_motor(E, M, speed):
    # Stop if in deadzone
    if DEADZONE_LOW <= speed <= DEADZONE_HIGH:
        E.duty_u16(0)
        return

    # Clamp speed
    speed = max(-MAX_SPEED, min(MAX_SPEED, speed))

    # Apply smooth curve for fine control
    sign = 1 if speed >= 0 else -1
    pwm_val = int(((abs(speed)/100)**2) * 65535)
    
    # Set motor values
    if speed > 0:
        M.value(0)              # Motor FORWARD
        E.duty_u16(pwm_val)     # Set motor duty cycle
    else:
        M.value(1)              # Motor BACKWARDS
        E.duty_u16(pwm_val)     # Set motor duty cycle

def stop_motors():
    E1.duty_u16(0)
    E2.duty_u16(0)

# ===============================
# HANDLE JOYSTICK DATA
# ===============================

def handle_command(cmd: bytes):         # Reading and using joystick data from transmitter
    """
    Expects format: "L:<adc_left>,R:<adc_right>"
    """
    # Decode data from transmitter
    try:
        msg = cmd.decode().strip()
        left_adc = int(msg.split(",")[0].split(":")[1])
        right_adc = int(msg.split(",")[1].split(":")[1])
    except Exception as e:
        print("Parse error:", e)
        stop_motors()
        return

    # Scale ADC 0-65535 → -100..100
    def scale_adc(val):
        speed = int((val / 65535) * 200 - 100)
        if DEADZONE_LOW <= speed <= DEADZONE_HIGH:
            return 0
        return speed

    # Get motor speeds
    left_speed = scale_adc(left_adc)
    right_speed = scale_adc(right_adc)

    # Set motor speeds
    set_motor(E1, M1, left_speed)
    set_motor(E2, M2, right_speed)

    # Use the line below for debugging
    #print(f"Left={left_speed}, Right={right_speed}")

# ===============================
# BLUETOOTH CONNECT
# ===============================

# DO NOT modify any code in this section, this handles Bluetooth communication.

async def find_remote():        # Finding bluetooth transmitter
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            if result.name() == _REMOTE_NAME:
                return result.device
    return None

async def connect_task():       # Connecting to bluetooth transmitter
    global connected
    while True:
        device = await find_remote()
        print("Connecting...")
        if not device:
            await asyncio.sleep(2)
            continue
        try:
            connection = await device.connect()
            print('Connected')
        except asyncio.TimeoutError:
            continue

        async with connection:
            connected = True
            led.on()            # Green LED on (blinking) when connected
            service = await connection.service(_GENERIC_SERVICE_UUID)
            characteristic = await service.characteristic(_JOYSTICK_CHARACTERISTIC_UUID)
            await characteristic.subscribe(notify=True)
            while True:
                try:
                    cmd = await characteristic.notified()
                    handle_command(cmd)
                except Exception as e:
                    print("Error:", e)
                    connected = False
                    led.off()
                    stop_motors()
                    break

        connected = False
        led.off()               # Green LED off when not connected
        stop_motors()           # Make sure motors turn off when connection is lost
        await asyncio.sleep(2)

# ===============================
# LED BLINKER
# ===============================

async def blink_task():             # LEDs blink while bluetooth connected
    toggle = True
    while True:
        led.value(toggle)           # Pico LED
        led_green.value(toggle)     # Green LED
        toggle = not toggle
        await asyncio.sleep_ms(250 if not connected else 1000)

# ===============================
# MAIN LOOP
# ===============================

async def main():
    await asyncio.gather(connect_task(), blink_task())

asyncio.run(main())