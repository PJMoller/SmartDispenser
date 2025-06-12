import board
import busio
import time
from lcd.lcd import LCD
from lcd.i2c_pcf8574_interface import I2CPCF8574Interface

# Initialize I2C pins and bus (SDA=GP0, SCL=GP1)
sda, scl = board.GP0, board.GP1
i2c = busio.I2C(scl, sda)

# Create LCD object for 20x4 display at I2C address 0x27
lcd = LCD(I2CPCF8574Interface(i2c, 0x27), num_rows=4, num_cols=20)

# Clear display
lcd.clear()

# Print message on line 0 (first line)
lcd.set_cursor_pos(0, 0)
lcd.print("Hello World!")

# Optionally keep the program running so you can see the message
while True:
    time.sleep(1)
