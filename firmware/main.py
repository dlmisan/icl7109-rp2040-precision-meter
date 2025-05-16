from machine import Pin, I2C
import ssd1306
from writer import Writer
from font.font10 import height, max_width, hmap, reverse, get_ch

class Font:
    def height(self): return height()
    def max_width(self): return max_width()
    def hmap(self): return hmap()
    def reverse(self): return reverse()
    def get_ch(self, ch): return get_ch(ch)
from utime import sleep_ms, ticks_ms, ticks_diff

i2c = I2C(0, scl=Pin(13), sda=Pin(12))
oled = ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3D)
wri = Writer(oled, Font())

STATUS_PIN = Pin(14, Pin.IN)
OR_PIN = Pin(16, Pin.IN)
POL_PIN = Pin(15, Pin.IN)
MC14052_A_PIN = Pin(10, Pin.OUT)
MC14052_B_PIN = Pin(11, Pin.OUT)

ADC_PINS = [
    Pin(28, Pin.IN),  # B1
    Pin(27, Pin.IN),
    Pin(26, Pin.IN),
    Pin(25, Pin.IN),
    Pin(24, Pin.IN),
    Pin(23, Pin.IN),
    Pin(22, Pin.IN),
    Pin(21, Pin.IN),
    Pin(20, Pin.IN),
    Pin(19, Pin.IN),
    Pin(18, Pin.IN),
    Pin(17, Pin.IN),  # B12
]

LED_PIN = Pin(2, Pin.OUT)
BUTTON_PIN = Pin(3, Pin.IN, Pin.PULL_UP)

MODE_AUTO = 0
MODE_Y2 = 1
MODE_Y3 = 2
current_mode = MODE_AUTO

VREF = 2.048
ADC_FULL_SCALE = 2048.0
DIVIDER_RATIO = 0.16694

def set_channel_voltage():
    MC14052_A_PIN.on()
    MC14052_B_PIN.off()

def set_channel_current():
    MC14052_A_PIN.off()
    MC14052_B_PIN.off()

def set_channel_y2():
    MC14052_A_PIN.off()
    MC14052_B_PIN.on()

def set_channel_y3():
    MC14052_A_PIN.on()
    MC14052_B_PIN.on()

def wait_status_low(timeout_ms=20):
    start = ticks_ms()
    while STATUS_PIN.value():
        if ticks_diff(ticks_ms(), start) > timeout_ms:
            return False
        sleep_ms(1)
    return True

def read_ic7109():
    adc_value = 0
    for i in range(12):
        if ADC_PINS[i].value():
            adc_value |= (1 << i)
    if not POL_PIN.value():
        adc_value = -adc_value
    return adc_value

def calculate_voltage(adc_value):
    measured_voltage = adc_value * (VREF / ADC_FULL_SCALE)
    return measured_voltage / DIVIDER_RATIO

def calculate_current(adc_value):
    measured_voltage = adc_value * (VREF / ADC_FULL_SCALE)
    return measured_voltage / 1.27

def calculate_voltage_y2(adc_value):
    measured_voltage = adc_value * (VREF / ADC_FULL_SCALE)
    return measured_voltage / DIVIDER_RATIO

def update_led():
    if current_mode == MODE_AUTO:
        LED_PIN.off()
    else:
        LED_PIN.on()

def read_button():
    if not BUTTON_PIN.value():
        sleep_ms(20)
        if not BUTTON_PIN.value():
            return True
    return False

def switch_mode():
    global current_mode
    current_mode = (current_mode + 1) % 3
    update_led()

def update_oled(mode_text, voltage=None, current=None):
    oled.fill(0)

    mode_x = (128 - wri.stringlen(mode_text)) // 2
    Writer.set_textpos(oled, 0, 0)
    font_h = wri.height
    text_w = wri.stringlen(mode_text)
    bg_x = (128 - text_w) // 2
    oled.fill_rect(bg_x - 4, 0, text_w + 10, font_h, 4)
    Writer.set_textpos(oled, 0, bg_x )
    wri.printstring(mode_text, invert=True)

    if voltage is not None:
        v_text = "{:.3f} V".format(voltage)
        v_x = (128 - wri.stringlen(v_text)) // 2
        Writer.set_textpos(oled, 26, v_x)  
        wri.printstring(v_text)

    if current is not None:
        c_text = "{:.2f} mA".format(current * 1000)
        c_x = (128 - wri.stringlen(c_text)) // 2
        Writer.set_textpos(oled, 46, c_x)  
        wri.printstring(c_text)

    oled.show()

def main():
    global current_mode
    print("ICL7109 voltage/current measurement")
    update_led()

    last_button_state = 1
    voltage = 0.0
    current = 0.0

    while True:
        current_button_state = BUTTON_PIN.value()
        if last_button_state and not current_button_state:
            switch_mode()
        last_button_state = current_button_state

        if current_mode == MODE_AUTO:
            set_channel_voltage()
            sleep_ms(130)
            if wait_status_low(100) and not OR_PIN.value():
                sleep_ms(3)
                adc = read_ic7109()
                voltage = calculate_voltage(adc)
                print("[Voltage] {:.3f} V".format(voltage))

            set_channel_current()
            sleep_ms(130)
            if wait_status_low(100) and not OR_PIN.value():
                sleep_ms(3)
                adc = read_ic7109()
                current = calculate_current(adc)
                print("[Current] {:.2f} mA".format(current * 1000))

            update_oled(" AUTO", voltage, current)

        elif current_mode == MODE_Y2:
            set_channel_y2()
            sleep_ms(130)
            if wait_status_low(100) and not OR_PIN.value():
                sleep_ms(3)
                adc = read_ic7109()
                voltage_y2 = calculate_voltage_y2(adc)
                print("[Y2 Channel] {:.3f} V".format(voltage_y2))
                update_oled(" Y2", voltage_y2)

        else:
            set_channel_y3()
            sleep_ms(130)
            if wait_status_low(100) and not OR_PIN.value():
                sleep_ms(3)
                adc = read_ic7109()
                print("[Y3 Channel] ADC: {}".format(adc))
                update_oled(" Y3")

        sleep_ms(50)

if __name__ == "__main__":
    main()
