import time
import board
import digitalio
from hx711 import HX711

# Setup HX711 pins
dout = digitalio.DigitalInOut(board.GP2)
pd_sck = digitalio.DigitalInOut(board.GP3)
hx = HX711(dout, pd_sck)

# Scale factor has been made by Scale_Factor_HX711_4Grams, calibrated using 4gram weights
scale_factor = -1060.0

hx.set_scale(scale_factor)

print("Put container on scale and press Enter to tare it...")
input()  # CHANGE TO BUTTON INPUT LATER
hx.tare()
print("Tare complete. Measuring contents weight now.")

while True:
    weight = hx.get_units(10)  # average 10 readings for smoothness
    print(f"Contents weight: {weight:.2f} g")
    time.sleep(1)
