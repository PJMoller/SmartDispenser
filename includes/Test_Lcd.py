from machine import Pin, I2C
from i2c_lcd import I2cLcd
from time import sleep

I2C_ADDR = 0x27  # replace with your scanned address if different

i2c = I2C(0, sda=Pin(0), scl=Pin(1))
lcd = I2cLcd(i2c, I2C_ADDR, 4, 20)

lcd.putstr("Hello from Pico!")
sleep(5)
lcd.clear()
lcd.putstr("PUMP ON")
