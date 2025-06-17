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
ALLOWED_DEVIATION_PERCENT = 2
STEP_OPTIONS = [1, 5, 10]

# Setup LCD
i2c = busio.I2C(scl=board.GP1, sda=board.GP0)
interface = I2CPCF8574Interface(i2c, 0x27)
lcd = LCD(interface, num_rows=4, num_cols=20)
lcd.backlight = True

# Motor control
in1 = digitalio.DigitalInOut(board.GP14)
in1.direction = digitalio.Direction.OUTPUT
in2 = digitalio.DigitalInOut(board.GP15)
in2.direction = digitalio.Direction.OUTPUT
ena = pwmio.PWMOut(board.GP13, frequency=1000, duty_cycle=0)

# Load cell
dout = digitalio.DigitalInOut(board.GP2)
pd_sck = digitalio.DigitalInOut(board.GP3)
hx = HX711(dout, pd_sck)
hx.set_scale(-1060.0)

# Buttons
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
    while button.value:
        time.sleep(0.01)

def select_volume(initial_step):
    volume = 0
    step_index = STEP_OPTIONS.index(initial_step)
    current_step = STEP_OPTIONS[step_index]
    lcd.clear()
    lcd.print("Set volume:")

    def update_display():
        lcd.set_cursor_pos(1, 0)
        lcd.print(f"Amount: {volume:>3} ml     ")
        lcd.set_cursor_pos(2, 0)
        lcd.print(f"Step: {current_step} ml     ")
        lcd.set_cursor_pos(3, 0)
        lcd.print("OK=Confirm Hold=Step")

    update_display()

    while True:
        if not btn_up.value:
            wait_for_button_press(btn_up)
            volume += current_step
            update_display()

        elif not btn_down.value:
            wait_for_button_press(btn_down)
            volume = max(0, volume - current_step)
            update_display()

        elif not btn_ok.value:
            press_time = time.monotonic()
            while not btn_ok.value:
                time.sleep(0.01)
            duration = time.monotonic() - press_time

            if duration > 1.0:
                step_index = (step_index + 1) % len(STEP_OPTIONS)
                current_step = STEP_OPTIONS[step_index]
                update_display()
            else:
                return volume

        time.sleep(0.1)

def dispense_ml(target_volume):
    total_dispensed = 0
    max_retries = 3  # om oneindige loops te voorkomen

    for attempt in range(max_retries):
        start_weight = get_weight()
        remaining_volume = target_volume - total_dispensed
        pump_time = remaining_volume / FLOW_RATE_PER_SEC

        lcd.clear()
        lcd.print("PUMP ON")
        lcd.set_cursor_pos(1, 0)
        lcd.print(f"Dispensing: {remaining_volume:.1f} ml")

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
        dispensed = abs(end_weight - start_weight)
        total_dispensed += dispensed

        deviation = abs(total_dispensed - target_volume) / target_volume * 100

        print(f"Expected: {target_volume:.1f} ml | Measured so far: {total_dispensed:.1f} g | Deviation: {deviation:.1f}%")

        
        if deviation <= ALLOWED_DEVIATION_PERCENT:
            lcd.clear()
            lcd.set_cursor_pos(0, 0)
            lcd.print(f"Dispensed: {target_volume:.1f}g")
            break
        else:
            if total_dispensed < target_volume:
                correction = target_volume - total_dispensed
                lcd.clear()
                lcd.set_cursor_pos(0, 0)
                lcd.print(f"Correcting: {correction:.1f}ml")
                time.sleep(2)

    time.sleep(10)



# Main loop
initial_step = 1
lcd.clear()
lcd.print("Ready to dispense")
while True:
    volume = select_volume(initial_step)
    dispense_ml(volume)

