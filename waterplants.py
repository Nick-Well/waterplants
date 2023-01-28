# iportrt av moduler som krävs för programets gång

import RPi.GPIO as GPIO
import time
import datetime
import Adafruit_ADS1x15
import os

# deklarering av variabler

adc = Adafruit_ADS1x15.ADS1115()
GAIN = 1
channel = 27
torr = 18000
watered = False
onAndOff = ""
adcv = 0
booli = ""

GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.OUT)

values = open("/home/pi/water/config.txt", "rb")
value_sline = values.readlines()[-1]
value = value_sline.split()
timeOutS = float(value[0])
pumpS = float(value[1])
sleepPumpS = float(value[2])
torr = int(value[3])
values.close()

# Beräkningar då time.sleep tar bara emot sekunder. och pumpen kontroleras också av en time.sleep vilket 1Dl=1.2sekund

timeout = timeOutS * 3600
sleepPump = sleepPumpS * 3600
pump = pumpS * 1.3


# oendlig loop som avbruts med control+C med hjälp av try~catch


def display():
    print("\033c")
    print("\n")
    print("Innan bevattning: " + str(timeOutS) + " Timmar.")
    print("Hur mycket vatten den pumper ut: " + str(pumpS) + " dl.")
    print("Efter bevattning paus: " + str(sleepPumpS) + " Timmar.")
    print("pumpen kommer gå igång när värdet är: " + str(torr))


def pump_if(booli):
    if booli == "ON":
        GPIO.output(channel, GPIO.HIGH)
        time.sleep(pump)
    else:
        GPIO.output(channel, GPIO.LOW)


def time_right_now():
    time = datetime.datetime.now().strftime("%X %d-%b-%Y")
    return time


def hour():
    hours = int(datetime.datetime.now().strftime("%H"))
    return hours


tid = hour()


def elses():
    pump_if("OFF")
    time.sleep(2.5)


def visa_adc():
    values = adc.read_adc(adcv, gain=GAIN)
    print("vid tiden: " + time_right_now())
    print(values)
    return str(values)


def logS(onAndOff):
    log = open("/home/pi/water/log.txt", "a")
    log.write(onAndOff + " vid tiden: " + time_right_now() + "\n")
    log.close()


def logV(onAndOff):
    log1 = open("/home/pi/water/values.txt", "rb")
    sistaRaden = log1.readlines()[-1]
    arrayRad = sistaRaden.split()
    delta = str(int(onAndOff) - int(arrayRad[1]))
    log1.close()
    log2 = open("/home/pi/water/values.txt", "a+")
    log2.write("värdet: " + onAndOff + " " + time_right_now() + " delta: " + delta + "\n")
    log2.close()


def config():
    values = open("/home/pi/water/config.txt", "rb")
    value_sline = values.readlines()[-1]
    value = value_sline.split()
    timeOutS = float(value[0])
    pumpS = float(value[1])
    sleepPumpS = float(value[2])
    torr = int(value[3])
    values.close()


def manuel():
    timeOutS = float(input("hur länge innan jorden är torr och den ska bevatnata jorden i timmar: "))
    pumpS = float(input("Hur många deseliter(DL) vatten ska växten ha per bevattning: "))
    sleepPumpS = float(input("hur länge efter bevattning ska pumpen sova i timmar: "))


def sleepAndShow(Sleeptime):
    for i in range(int(Sleeptime)):
        values = adc.read_adc(adcv, gain=GAIN)
        display()
        print("\n")
        print("minuter kvar: " + str("%.1f" % ((Sleeptime - i) / 60)))
        print("\n")
        visaADC()
        time.sleep(1)


while True:
    try:
        # värdet från vatten sensorn som konverteras i ADC:n
        values = adc.read_adc(adcv, gain=GAIN)
        if hour() != tid:
            logV(str(values))
            tid = hour()

        display()
        if hour() in range(9, 20):
            print("\n\n\n\n")
            visaADC()
            if watered == False:

                # om värdet från sensorn störe en 6900 så kommer den köra det under annars hoppar den över till else

                if values >= torr:
                    sleepAndShow(timeout)
                    pump_if("ON")

                    # paus melan bevatningarna görs med en if statement innan dena

                    watered = True
                    pump_if("OFF")

                    # log fil när den har vatnat
                    logS("bevatnats")
                else:
                    elses()
            else:
                print("sover " + time_right_now())
                sleepAndShow(sleepPump)
                logS("sattigång")
                watered = False
        else:
            print("\n")
            print("sover")
            print("\n")
            visaADC()
            elses()

    except KeyboardInterrupt:
        break
GPIO.cleanup()
print(" god natt!! ")
