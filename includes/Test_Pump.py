from machine import Pin, PWM
from time import sleep

in1 = Pin(14, Pin.OUT)
in2 = Pin(15, Pin.OUT)
enable = PWM(Pin(13))

# Set PWM frequency
enable.freq(1000)  # 1 kHz for motor control

def pump_on(speed):
    enable.duty_u16(speed)  # Speed (0 to 65535)
    in1.value(0)
    in2.value(1)
    print("Pump ON")

def pump_off():
    enable.duty_u16(0)  # Stop PWM
    in1.value(0)
    in2.value(0)
    print("Pump OFF")

try:
    while True:
        pump_on(65535) 
        sleep(50)
        pump_off()
        sleep(1)
except KeyboardInterrupt:
    pump_off()
