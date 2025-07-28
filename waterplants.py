
import RPi.GPIO as GPIO
import time
import datetime
import Adafruit_ADS1x15

adc = Adafruit_ADS1x15.ADS1115()
GAIN = 1
channel = 27
dry_sensor = 18000
watered = False
adcv = 0

# hour in the day
start_sensor = 9
stop_sensor = 22


GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.OUT)

with open("/home/pi/water/config.txt", "rb") as values:
    value_sline = values.readlines()[-1]
    value = value_sline.split()
    timeOutS = float(value[0])
    pumpS = float(value[1])
    sleepPumpS = float(value[2])
    dry_sensor = int(value[3])

timeout = timeOutS * 3600
sleepPump = sleepPumpS * 3600
aktivePumpTime = pumpS * 1.3


def display():
    print("\033c")
    print("\n")
    print("Before watering: " + str(timeOutS) + " hours.")
    print("Amount of water pumped out: " + str(pumpS) + " dl.")
    print("After watering pause: " + str(sleepPumpS) + " hours.")
    print("The pump will turn on when the value is: " + str(dry_sensor))


def pump_active(state):
    GPIO.output(channel, GPIO.HIGH if state else GPIO.LOW)
    if state:
        time.sleep(aktivePumpTime)


def get_current_time():
    return datetime.datetime.now().strftime("%X %d-%b-%Y")


def get_current_hour():
    return int(datetime.datetime.now().strftime("%H"))


current_hour = get_current_hour()


def display_adc_value():
    value = adc.read_adc(adcv, gain=GAIN)
    print("At the time: " + get_current_time() + "\n" + value)
    return str(value)


def log_state(state):
    with open("/home/pi/water/log.txt", "a") as log:
        log.write(state + " at the time: " + get_current_time() + "\n")


def log_value(value):
    with open("/home/pi/water/values.txt", "a+") as log:
        with open("/home/pi/water/values.txt", "rb") as log1:
            last_line = log1.readlines()[-1]
            value_array = last_line.split()
            delta = str(int(value) - int(value_array[1]))
        log.write("value: " + value + " " + get_current_time() + " delta: " + delta + "\n")


def config():
    with open("/home/pi/water/config.txt", "rb") as values:
        value_sline = values.readlines()[-1]
        value = value_sline.split()
        timeOutS = float(value[0])
        pumpS = float(value[1])
        sleepPumpS = float(value[2])
        dry_sensor = int(value[3])


def manuel():
    timeOutS = float(input("How long before the soil is dry and water it (hours): "))
    pumpS = float(input("How many deciliters (DL) of water should the plant have per watering: "))
    sleepPumpS = float(input("How long after watering should the pump sleep (hours): "))


def sleepAndShow(inactive_timer):
    for i in range(int(inactive_timer)):
        values = adc.read_adc(adcv, gain=GAIN)
        display()
        print("\n Minutes remaining: " + str("%.1f" % ((inactive_timer - i) / 60)) + "\n")
        display_adc_value()
        time.sleep(1)


def is_daytime():
    return start_sensor <= get_current_hour() < stop_sensor


def sleep_and_show(timeout):
    sleepAndShow(timeout)


def check_moisture_level():
    values = adc.read_adc(adcv, gain=GAIN)
    if values >= dry_sensor:
        return True
    return False


def watering_routine():
    pump_active(True)
    log_state("watered")
    sleep_and_show(timeout)
    pump_active(False)


def saturation_routine():
    log_state("saturation")
    sleep_and_show(sleepPump)


watered = False
while True:
    try:
        display()
        display_adc_value()
        if is_daytime():
            if not watered:
                if check_moisture_level():
                    watering_routine()
                    watered = True
                else:
                    pump_active(False)
            else:
                saturation_routine()
                watered = False
        else:
            print("sleeping")
            display_adc_value()
            pump_active(False)

        current_hour = get_current_hour()
        if current_hour != tid:
            log_value(values)
            tid = current_hour
    except KeyboardInterrupt:
        break
GPIO.cleanup()
print(" god natt!! ")

