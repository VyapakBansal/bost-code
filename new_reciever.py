import aioble
import bluetooth
import uasyncio as asyncio
from machine import Pin, PWM
import time

# ===============================
# RECEIVER CONFIG
# ===============================

_REMOTE_NAME = "B2_C5"
_GENERIC_SERVICE_UUID = bluetooth.UUID(0x1848)
_JOYSTICK_CHARACTERISTIC_UUID = bluetooth.UUID(0x2A6E)

connected = False
led = Pin("LED", Pin.OUT)
led_green = Pin(2, Pin.OUT)

# ===============================
# MOTOR PINS (L298N)
# ===============================

E1 = PWM(Pin(0))
M1 = Pin(1, Pin.OUT)
E2 = PWM(Pin(3))
M2 = Pin(4, Pin.OUT)

E1.freq(500)
E2.freq(500)

# SAFE STARTUP STATE
E1.duty_u16(0)
E2.duty_u16(0)
M1.value(0)
M2.value(0)

# ===============================
# SETTINGS
# ===============================

DEADZONE_LOW = -10
DEADZONE_HIGH = 10
MAX_SPEED = 100

last_command_time = time.ticks_ms()

# ===============================
# MOTOR CONTROL
# ===============================

def set_motor(E, M, speed):
    if DEADZONE_LOW <= speed <= DEADZONE_HIGH:
        E.duty_u16(0)
        return

    speed = max(-MAX_SPEED, min(MAX_SPEED, speed))

    pwm_val = int(((abs(speed)/100)**2) * 65535)

    if speed > 0:
        M.value(0)
        E.duty_u16(pwm_val)
    else:
        M.value(1)
        E.duty_u16(pwm_val)

def stop_motors():
    E1.duty_u16(0)
    E2.duty_u16(0)

# ===============================
# HANDLE JOYSTICK DATA
# ===============================

def handle_command(cmd: bytes):
    global last_command_time

    try:
        msg = cmd.decode().strip()
        left_adc = int(msg.split(",")[0].split(":")[1])
        right_adc = int(msg.split(",")[1].split(":")[1])
    except:
        stop_motors()
        return

    def scale_adc(val):
        speed = int((val / 65535) * 200 - 100)
        if DEADZONE_LOW <= speed <= DEADZONE_HIGH:
            return 0
        return speed

    left_speed = scale_adc(left_adc)
    right_speed = scale_adc(right_adc)

    set_motor(E1, M1, left_speed)
    set_motor(E2, M2, right_speed)

    last_command_time = time.ticks_ms()

# ===============================
# BLUETOOTH
# ===============================

async def find_remote():
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            if result.name() == _REMOTE_NAME:
                return result.device
    return None

async def connect_task():
    global connected

    while True:
        device = await find_remote()
        print("Connecting...")

        if not device:
            await asyncio.sleep(2)
            continue

        try:
            connection = await device.connect()
            print("Connected")
        except asyncio.TimeoutError:
            continue

        async with connection:
            connected = True
            led.on()
            stop_motors()  # IMPORTANT: stop on connect

            service = await connection.service(_GENERIC_SERVICE_UUID)
            characteristic = await service.characteristic(_JOYSTICK_CHARACTERISTIC_UUID)
            await characteristic.subscribe(notify=True)

            packet_count = 0

            while True:
                try:
                    cmd = await characteristic.notified()

                    # Ignore first few packets (garbage values)
                    if packet_count < 3:
                        packet_count += 1
                        stop_motors()
                        continue

                    handle_command(cmd)

                except Exception as e:
                    print("Error:", e)
                    connected = False
                    led.off()
                    stop_motors()
                    break

        connected = False
        led.off()
        stop_motors()
        await asyncio.sleep(2)

# ===============================
# SAFETY TIMEOUT
# ===============================

async def safety_task():
    global last_command_time

    while True:
        if time.ticks_diff(time.ticks_ms(), last_command_time) > 500:
            stop_motors()
        await asyncio.sleep_ms(100)

# ===============================
# LED BLINK
# ===============================

async def blink_task():
    toggle = True
    while True:
        led.value(toggle)
        led_green.value(toggle)
        toggle = not toggle
        await asyncio.sleep_ms(250 if not connected else 1000)

# ===============================
# MAIN
# ===============================

async def main():
    await asyncio.gather(connect_task(), blink_task(), safety_task())

asyncio.run(main())