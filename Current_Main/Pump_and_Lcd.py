from machine import Pin, PWM, I2C
from time import sleep
from i2c_lcd import I2cLcd

# LCD setup
I2C_ADDR = 0x27
i2c = I2C(0, scl=Pin(1), sda=Pin(0))
lcd = I2cLcd(i2c, I2C_ADDR, 4, 20)

# Motor control pins
in1 = Pin(14, Pin.OUT)
in2 = Pin(15, Pin.OUT)
enable = PWM(Pin(13))
enable.freq(1000)

# Pump flow rate (ml/min)
FLOW_RATE = 39  # ml per minute
FLOW_RATE_PER_SEC = FLOW_RATE / 60  # ml per second

def pump_on(speed=65535):
    enable.duty_u16(speed)
    in1.value(1)
    in2.value(0)

def pump_off():
    enable.duty_u16(0)
    in1.value(0)
    in2.value(0)

def dispense_ml(volume):
    pump_time = volume / FLOW_RATE_PER_SEC
    lcd.clear()
    print(f"Dispensing {volume} ml in {pump_time:.2f} seconds")
    pump_on()
    
    lcd.move_to(0, 0)
    lcd.putstr("PUMP ON")
    lcd.move_to(0, 1)
    lcd.putstr(f"Dispensing: {volume} ml")

    # Countdown and display time remaining
    for remaining in range(int(pump_time), 0, -1):
        lcd.move_to(0, 2)
        lcd.putstr(f"Time left: {remaining:2d} sec")
        print(f"Time left: {remaining} sec")
        sleep(1)

    pump_off()
    lcd.clear()
    lcd.putstr("Done!")
    sleep(5)  

while True:
    lcd.clear()
    lcd.putstr("Enter amount (ml):")
    desired_ml = float(input("Enter amount (ml): "))
    dispense_ml(desired_ml)

