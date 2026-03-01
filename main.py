from machine import Pin, I2C, ADC
from ssd1306 import SSD1306_I2C
from image import *
import time

# --- OLED ---
i2c = I2C(scl=Pin(5), sda=Pin(4))
oled = SSD1306_I2C(128, 64, i2c)

# --- Кнопки ---
btn_up = Pin(12, Pin.IN, Pin.PULL_UP)
btn_down = Pin(14, Pin.IN, Pin.PULL_UP)
btn_select = Pin(0, Pin.IN, Pin.PULL_UP)
pump = Pin(13, Pin.OUT) 

# --- Датчик вологості ---
soil_sensor = ADC(0)  # A0

# --- Змінні ---
desired_humidity = 50
current_humidity = 0
drySensor = 684
wetSensor = 472
dropSign = False

start = ["Settings", "Controll", "Plants Info", "Back"]
settings = ["Manual", "Presets", "Back"]
controll = ['Turn on pump', 'Turn off pump', 'By target', 'Back']
manual = ['Set target', 'Set sleep time', 'Set name', 'Back']

Name = 'Infusoria'
plantMood = 'Feels good!'
state = "main"  # main / start / settings
title = ['Start']
history = [start]
selected = 0
anim = playPlant(oled, 4, 16)

# --- Функції ---
def wait_release(pin):
    while not pin.value():
        time.sleep(0.01)

def drawProgressBar(value, x = 32, y = 22):
    oled.rect(x, y, 64, 11, 1)
    lineLength = int(value * 60 / 100)

    for i in range(2, 9):
        oled.hline(x + 2, y + i, lineLength, 1)

def read_soil():
    raw = soil_sensor.read()
    if raw <= wetSensor:
        percent = 100
    elif raw >= drySensor:
        percent = 0
    else:
        percent = int((drySensor - raw)/(drySensor - wetSensor) * 100)
    return percent

def checkMoisture():
    global dropSign, plantMood 
    if current_humidity < desired_humidity:
        pump.on()
        dropSign = True
    elif current_humidity >= desired_humidity:
        pump.off()
        dropSign = False

    if current_humidity - desired_humidity > 10:
        plantMood = 'is overwet'
    elif desired_humidity - current_humidity > 10:
        plantMood = 'is thirsty'
    else:
        plantMood = 'Feels good!'

def show_main():
    oled.fill(0)
    checkMoisture()
    oled.text("Soil:{}% T:{}%".format(current_humidity, desired_humidity), 0, 0)
    oled.hline(0, 9, 128, 1)
    next(anim)
    oled.text('{}'.format(Name), 40, 22)
    oled.text('{}'.format(plantMood), 40, 35)
    oled.hline(0, 52, 128, 1)
    if dropSign:
        draw(oled, drop, 0, 63-7)
    oled.text(">Start", 78, 64-9)
    oled.show()

def show_menu(menu):
    oled.fill(0)
    oled.text(title[-1] + ' menu:', 0, 0)
    oled.hline(0, 9, 128, 1)
    for i, item in enumerate(menu):
        prefix = ">" if i == selected else " "
        oled.text(prefix + item, 0, i * 10 + 11)
    oled.show()

def set_target():
    global desired_humidity
    while True:
        oled.fill(0)
        oled.text("Set target:", 0, 0)
        oled.hline(0, 9, 128, 1)
        drawProgressBar(desired_humidity)
        oled.text("{}%".format(desired_humidity), 52, 35)
        oled.hline(10, 63-10, 108, 1)
        oled.text("Press SELECT", 16, 63-8)
        oled.hline(10, 63, 108, 1)
        oled.show()

        if not btn_up.value():
            desired_humidity = min(100, desired_humidity + 1)

        if not btn_down.value():
            desired_humidity = max(0, desired_humidity - 1)

        if not btn_select.value():
            wait_release(btn_select)
            break

# --- Головний цикл ---
while True:
    current_humidity = read_soil()

    if state == "main":
        show_main()

        if not btn_select.value():
            wait_release(btn_select)
            state = "start"
            selected = 0

    elif state == "start":
        show_menu(history[-1])

        if not btn_up.value():
            selected = (selected - 1) % len(history[-1])
            wait_release(btn_up)

        if not btn_down.value():
            selected = (selected + 1) % len(history[-1])
            wait_release(btn_down)

        if not btn_select.value():
            wait_release(btn_select)

            if history[-1][selected] == "Settings":
                history.append(settings)
                title.append('Settings')
                selected = 0

            elif history[-1][selected] == "Controll":
                history.append(controll)
                title.append('Controll')
                selected = 0
            
            elif history[-1][selected] == "Manual":
                history.append(manual)
                title.append('Manual')
                selected = 0
            
            elif history[-1][selected] == "Set target":
                set_target()
            
            elif history[-1][selected] == "Turn on pump":
                pump.on()

            elif history[-1][selected] == "Turn off pump":
                pump.off()

            elif history[-1][selected] == "Back":
                if history[-1] == start:
                    state = 'main'
                else:
                    history.pop()
                    title.pop()
                    selected = 0
