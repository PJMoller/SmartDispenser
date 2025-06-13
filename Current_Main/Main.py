import time
import board
import pwmio
import digitalio
import busio
from lcd.lcd import LCD
from lcd.i2c_pcf8574_interface import I2CPCF8574Interface
from hx711 import HX711

# Constants
FLOW_RATE = 39  # ml/min
FLOW_RATE_PER_SEC = FLOW_RATE / 60
ALLOWED_DEVIATION_PERCENT = 5
STEP_OPTIONS = [5, 10, 20]

# Setup LCD
i2c = busio.I2C(scl=board.GP1, sda=board.GP0)
lcd = LCD(I2CPCF8574Interface(i2c, 0x27), num_rows=4, num_cols=20)

# Motor control
in1 = digitalio.DigitalInOut(board.GP14)
in1.direction = digitalio.Direction.OUTPUT
in2 = digitalio.DigitalInOut(board.GP15)
in2.direction = digitalio.Direction.OUTPUT
ena = pwmio.PWMOut(board.GP13, frequency=1000, duty_cycle=0)

# Load cell (HX711)
dout = digitalio.DigitalInOut(board.GP2)
pd_sck = digitalio.DigitalInOut(board.GP3)
hx = HX711(dout, pd_sck)
hx.set_scale(-1060.0)

# Buttons (with internal pull-ups)
btn_up = digitalio.DigitalInOut(board.GP6)
btn_up.direction = digitalio.Direction.INPUT
btn_up.pull = digitalio.Pull.UP

btn_down = digitalio.DigitalInOut(board.GP7)
btn_down.direction = digitalio.Direction.INPUT
btn_down.pull = digitalio.Pull.UP

btn_ok = digitalio.DigitalInOut(board.GP8)
btn_ok.direction = digitalio.Direction.INPUT
btn_ok.pull = digitalio.Pull.UP

# Functions
def pump_on(speed=65535):
    in1.value = True
    in2.value = False
    ena.duty_cycle = speed

def pump_off():
    ena.duty_cycle = 0
    in1.value = False
    in2.value = False

def get_weight():
    return hx.get_units(10)

def wait_for_button_press(button):
    while button.value:  # Wait until button is pressed (LOW)
        time.sleep(0.01)

def choose_step_size():
    index = 0
    lcd.clear()
    lcd.print("Choose step size:")

    def display_options(selected_index):
        for i, step in enumerate(STEP_OPTIONS):
            lcd.set_cursor_pos(i + 1, 0)
            if i == selected_index:
                lcd.print(f"> {step} ml        ")
            else:
                lcd.print(f"  {step} ml        ")

    display_options(index)

    while True:
        if not btn_up.value:
            wait_for_button_press(btn_up)
            index = (index - 1) % len(STEP_OPTIONS)  # Move up
            display_options(index)

        elif not btn_down.value:
            wait_for_button_press(btn_down)
            index = (index + 1) % len(STEP_OPTIONS)  # Move down
            display_options(index)

        elif not btn_ok.value:
            wait_for_button_press(btn_ok)
            return STEP_OPTIONS[index]  # Confirm selection

        time.sleep(0.1)


def select_volume(step):
    volume = 0
    lcd.clear()
    lcd.print("Set volume:")
    while True:
        lcd.set_cursor_pos(1, 0)
        lcd.print(f"Amount: {volume:>3} ml     ")
        lcd.set_cursor_pos(2, 0)
        lcd.print("OK = Confirm    ")
        if not btn_up.value:
            wait_for_button_press(btn_up)
            volume += step
        elif not btn_down.value:
            wait_for_button_press(btn_down)
            volume = max(0, volume - step)
        elif not btn_ok.value:
            wait_for_button_press(btn_ok)
            return volume
        time.sleep(0.1)

def dispense_ml(volume):
    start_weight = get_weight()
    pump_time = volume / FLOW_RATE_PER_SEC

    lcd.clear()
    lcd.print("PUMP ON")
    lcd.set_cursor_pos(1, 0)
    lcd.print(f"Dispensing: {volume:.1f} ml")

    pump_on()
    for remaining in range(int(pump_time), 0, -1):
        lcd.set_cursor_pos(2, 0)
        lcd.print(f"Time left: {remaining:2d} sec    ")
        time.sleep(1)

    extra = pump_time - int(pump_time)
    if extra > 0:
        time.sleep(extra)

    pump_off()
    lcd.clear()
    lcd.print("Measuring...")
    time.sleep(2)

    end_weight = get_weight()
    dispensed = end_weight - start_weight
    deviation = abs(dispensed - volume) / volume * 100

    lcd.clear()
    if deviation > ALLOWED_DEVIATION_PERCENT:
        lcd.print(f"~{volume:.1f} ml dispensed")
    else:
        lcd.print(f"{volume:.1f} ml dispensed")
    print(f"Expected: {volume:.1f} ml | Measured: {dispensed:.1f} g | Deviation: {deviation:.1f}%")
    time.sleep(4)

# Start
lcd.clear()
lcd.print("Place empty cup")
lcd.set_cursor_pos(1, 0)
lcd.print("Press OK to tare")
wait_for_button_press(btn_ok)
lcd.clear()
lcd.print("Taring...")
hx.tare()
lcd.set_cursor_pos(1, 0)
lcd.print("Tare complete")
time.sleep(2)

# Main loop
while True:
    step = choose_step_size()
    volume = select_volume(step)
    dispense_ml(volume)


