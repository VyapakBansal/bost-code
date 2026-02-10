import aioble
import bluetooth
import uasyncio as asyncio
from micropython import const
from machine import ADC, Pin

# RENAME THIS FILE TO main.py WHEN SAVING TO THE PI PICO (Controller)

# ===============================
# TRANSMITTER CONFIG
# ===============================

_DEVICE_NAME = "engg_200"                               # Your group name, i.e 'B1_A1' for Block 1, Group A1
_GENERIC_SERVICE_UUID = bluetooth.UUID(0x1848)          
_JOYSTICK_CHARACTERISTIC_UUID = bluetooth.UUID(0x2A6E) 
_ADV_INTERVAL_MS = 250_000
_BLE_APPEARANCE_GENERIC_REMOTE_CONTROL = const(384)

# ===============================
# HARDWARE SETUP
# ===============================

# Make sure pin numbers match wiring

adc_left = ADC(27)          # Left joystick vertical
adc_right = ADC(26)         # Right joystick vertical
led = Pin("LED", Pin.OUT)   # LED on Pi Pico

# Set default as disconnected
connected = False
connection = None

# ===============================
# BLE SERVICE
# ===============================

remote_service = aioble.Service(_GENERIC_SERVICE_UUID)
joystick_char = aioble.Characteristic(remote_service,
                                       _JOYSTICK_CHARACTERISTIC_UUID,
                                       read=True,
                                       notify=True)
aioble.register_services(remote_service)

# ===============================
# BLE TASKS
# ===============================

# DO NOT modify either advertise_task() or blink_task() unless absoloutely required.

async def advertise_task():     # Connecting to bluetooth receiver
    global connected, connection
    while True:
        connected = False
        async with await aioble.advertise(_ADV_INTERVAL_MS,
                                          name=_DEVICE_NAME,
                                          appearance=_BLE_APPEARANCE_GENERIC_REMOTE_CONTROL,
                                          services=[_GENERIC_SERVICE_UUID]) as connection:
            connected = True
            await connection.disconnected()

async def joystick_task():      # Sending joystick data to receiver
    global connected
    last_left = last_right = -1
    while True:
        # Read data if connected
        if connected:
            left_val = adc_left.read_u16()
            right_val = adc_right.read_u16()

            # IF ADDING NEW COMPONENTS, READ INPUTS HERE.

            # Send only if changed
            if left_val != last_left or right_val != last_right:
                msg = f"L:{left_val},R:{right_val}"
                joystick_char.notify(connection, msg.encode())
                last_left, last_right = left_val, right_val
                print("Sent →", msg)

        await asyncio.sleep_ms(50)

async def blink_task():     # Pico LED blinks when bluetooth connected
    toggle = True
    while True:
        led.value(toggle)
        toggle = not toggle
        await asyncio.sleep_ms(1000 if connected else 250)

# ===============================
# MAIN LOOP
# ===============================

async def main():
    await asyncio.gather(advertise_task(), joystick_task(), blink_task())

asyncio.run(main())