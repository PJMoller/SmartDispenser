from machine import Pin
from time import sleep
from hx711 import HX711

hx = HX711(d_out=Pin(16), pd_sck=Pin(17))

while True:
    val = hx.read()
    print("Raw reading:", val)
    sleep(0.5)
