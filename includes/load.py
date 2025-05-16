from hx711 import HX711
import RPi.GPIO as GPIO

def getReadings():
    try:
        hx711 = HX711(
            dout_pin=5,
            pd_sck_pin=6,
            channel='A',
            gain=64
        )

        hx711.reset()
        measures = hx711.get_raw_data(num_measures=3)
    finally:
        GPIO.cleanup()

    print("\n".join(measures))