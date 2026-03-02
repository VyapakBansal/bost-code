from machine import Pin, PWM, ADC
import aioble
import bluetooth
import uasyncio as asyncio
from micropython import const

# ===============================
# MOTOR SETUP
# ===============================
E1 = PWM(Pin(0))   # Left motor PWM
M1 = Pin(1, Pin.OUT)

E2 = PWM(Pin(3))   # Right motor PWM
M2 = Pin(4, Pin.OUT)

E1.freq(500)
E2.freq(500)

# ===============================
# BLE SETUP
# ===============================
_DEVICE_NAME = "B2_C5"
_GENERIC_SERVICE_UUID = bluetooth.UUID(0x1848)
_JOYSTICK_CHARACTERISTIC_UUID = bluetooth.UUID(0x2A6E)
_ADV_INTERVAL_MS = 250_000
_BLE_APPEARANCE_GENERIC_REMOTE_CONTROL = const(384)

connected = False
connection = None

remote_service = aioble.Service(_GENERIC_SERVICE_UUID)
joystick_char = aioble.Characteristic(
    remote_service,
    _JOYSTICK_CHARACTERISTIC_UUID,
    read=True,
    notify=True
)

aioble.register_services(remote_service)

# ===============================
# JOYSTICK SETUP
# ===============================
adc_x = ADC(27)
adc_y = ADC(26)
sw = Pin(22, Pin.IN, Pin.PULL_UP)

# Shared state variables
x_dir = "middle"
y_dir = "middle"

# ===============================
# BLE ADVERTISE TASK
# ===============================
async def advertise_task():
    global connected, connection
    while True:
        connected = False
        async with await aioble.advertise(
            _ADV_INTERVAL_MS,
            name=_DEVICE_NAME,
            appearance=_BLE_APPEARANCE_GENERIC_REMOTE_CONTROL,
            services=[_GENERIC_SERVICE_UUID],
        ) as connection:
            connected = True
            await connection.disconnected()

# ===============================
# JOYSTICK TASK
# ===============================
async def joystick_task():
    global connected, connection

    while True:
        if connected:
            left_adc = adc_x.read_u16()
            right_adc = adc_y.read_u16()

            msg = f"L:{left_adc},R:{right_adc}"
            joystick_char.notify(connection, msg.encode())

        await asyncio.sleep_ms(50)

# # ===============================
# # MOTOR TASK
# # ===============================
# async def motor_task():
#     global x_dir, y_dir

#     while True:
#         # Left motor controlled by X
#         if x_dir == "left":
#             M1.value(1)
#             E1.duty_u16(40000)
#         elif x_dir == "right":
#             M1.value(0)
#             E1.duty_u16(40000)
#         else:
#             E1.duty_u16(0)

#         # Right motor controlled by Y
#         if y_dir == "up":
#             M2.value(1)
#             E2.duty_u16(40000)
#         elif y_dir == "down":
#             M2.value(0)
#             E2.duty_u16(40000)
#         else:
#             E2.duty_u16(0)

#         await asyncio.sleep_ms(50)

# ===============================
# LED BLINK TASK
# ===============================
async def blink_task():
    led = Pin("LED", Pin.OUT)
    toggle = False

    while True:
        led.value(toggle)
        toggle = not toggle
        await asyncio.sleep_ms(1000 if connected else 250)

# ===============================
# MAIN
# ===============================
async def main():
    await asyncio.gather(
        advertise_task(),
        joystick_task(),
        blink_task()
    )

asyncio.run(main())