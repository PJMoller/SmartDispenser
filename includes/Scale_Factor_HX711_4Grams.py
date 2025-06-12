import time
import board
import digitalio
from hx711 import HX711

dout = digitalio.DigitalInOut(board.GP2)
pd_sck = digitalio.DigitalInOut(board.GP3)

hx = HX711(dout, pd_sck)

print("Taring...")
hx.tare()
print("Tared.")

tare_val = hx.read_raw()
print("Tare raw value:", tare_val)

print("Place 4g weight...")
time.sleep(5)

reading = hx.read_raw()
print("Raw reading with 4g weight:", reading)

scale = (reading - tare_val) / 4.0
print("Calculated scale factor:", scale)

hx.set_scale(scale)

while True:
    weight = hx.get_units(10)
    print(f"Weight: {weight:.2f} g")
    time.sleep(1)
