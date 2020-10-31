# Welcome to Greenearth's ContainerPi!

# This is a remote control and automated
# controller that operates a 40' container greenhouse. The microcontroller
# is wired to sensors that measure the environment and then uses this data
# to operate digital relays. These digtal relays control the electrical
# panel inside the container which switches on lights, CO2 regulator, heater
# and can be adapted to control pumps for watering and nutrients, load cells
# that measure the plants growth and HVAC systems.

#Future work includes storing these data points in a SQL database and
#running machine learning algorithms on these data points to optimize the
#operation of the relays. Eventually photographs of plants at their different
#lifecycles will be incoporated to visually identify disease, and use life cycle
#data to operate specific programs based on their needs. Machine learning and
#deep-learning algorithms can be used to process images and the database to further
#optimize the control and growth of the plants.

#Importing libraries and modules

import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import RPi.GPIO as GPIO
import time
import datetime
from random import randint
from datetime import timedelta
from scd30_i2c import SCD30

#initializing the C02 sensor

scd30 = SCD30()

scd30.set_measurement_interval(2)
scd30.start_periodic_measurement()
time.sleep(2)  # this is how often we sample the sensor (seconds)

#Defining the variables for the relays and their GPIOs
#RELAYS and RPi GPIOS

CO2 = 18     #relay IN1 input for C02 regulator on GPIO 18
LED1 = 12    #relay IN2 input contactor for the fluence LEDs f1+f2 & f5+f6 on GPIO 12
LED2 = 25    #relay IN3 input contactor for the fluence LEDs f3+f4 & f7+f8 on GPIO 25
MARS = 23    #relay IN4 input contactor for the 8 Mars on three circuit breakers GPIO 23
HEATER = 24  #relay IN5 input for the heater GPIO 24

#Initializing RPi GPIO addresses for relays


GPIO.setmode(GPIO.BCM) # We state we are using Broadcom's chipset mapping to identify the GPIOs
GPIO.setup(CO2, GPIO.OUT) #setting up our output from the chipset
GPIO.setup(LED1, GPIO.OUT)
GPIO.setup(LED2, GPIO.OUT)
GPIO.setup(MARS, GPIO.OUT)
GPIO.setup(HEATER, GPIO.OUT)
 
# create the spi bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
 
# create the cs (chip select)
cs = digitalio.DigitalInOut(board.D5)
 
# create the mcp object
mcp = MCP.MCP3008(spi, cs)
 
# create an analog input channel on pin 0
chan0 = AnalogIn(mcp, MCP.P0)

#########################################################################
#This is the code for the digital light timers that turn on/off lights  #
#at the same times every day. This loops forever                        #
#########################################################################

localtime = time.asctime( time.localtime(time.time()) )
print(time.asctime( time.localtime(time.time()) ))

    
#Define relay 'on' times
ONHOUR = 7
ONMIN = 30 #We can add additional on times and offset each one by a few seconds to prevent power surges
ONSEC = randint(5, 15) #We can also individually code unique on off times for each relay if desired

#Define relay 'off' times
OFFHOUR = 19
OFFMIN = 30
OFFSEC = randint(5, 15) #roughly 1/60 chance both sets of lights will come on at the same time

#Define relay on times
ONHOUR2 = 7
ONMIN2 = 30 
ONSEC2 = randint(5, 15)

#Define relay off times
OFFHOUR2 = 19
OFFMIN2 = 30
OFFSEC2 = randint(5, 15)

#Define relay on times
#ONHOUR3 = 7
#ONMIN3 = 30 
#ONSEC3 = randint(5, 15)

#Define relay off times
#OFFHOUR3 = 19
#OFFMIN3 = 30
#OFFSEC3 = randint(5, 15)


#########################################################################
# This loop operates while the sensors are producing measurements,"m"   #  
# Measuresments are stored in an array m[]. The program runs until      #
# there is no reading. The relays are controlled based on the m[] matrix#
#########################################################################

while True:
    if scd30.get_data_ready():
        m = scd30.read_measurement()
        dt = list(time.localtime())
        hour = dt[3]
        minute = dt[4]
        second = dt[5]
        time.sleep(1)        
        if m is not None:
            print(f"Time{hour,minute,second},[CO2]: {m[0]:.2f}ppm, Temperature: {m[1]:.2f}C, Humidity: {m[2]:.2f}%, Moisture Value: {chan0.value}, Moisture Voltage: {chan0.voltage:.2f}V")
            #print(hour,minute,second)
        
        time.sleep(2)        
        
        if m[0]<1800: 
            GPIO.output(CO2, GPIO.LOW)

        else:
            GPIO.output(CO2, GPIO.HIGH)
        
        if m[1]<22: 
            GPIO.output(HEATER, GPIO.LOW)

        else:
            GPIO.output(HEATER, GPIO.HIGH)
        
            if m is not None:
              
              if hour == ONHOUR: #if the time counter matches the ON/OFF time activate the relays
                    if minute == ONMIN:
                      if second == ONSEC:
                        GPIO.output(LED1, GPIO.LOW)
                        GPIO.output(LED2, GPIO.LOW)
                        #GPIO.output(MARS, GPIO.LOW)
            
              if hour == OFFHOUR:
                    if minute == OFFMIN:
                      if second == OFFSEC:
                        GPIO.output(LED1, GPIO.HIGH)
                        GPIO.output(LED2, GPIO.HIGH)
                        #GPIO.output(MARS, GPIO.HIGH)
                        
              if hour == ONHOUR2: 
                    if minute == ONMIN2:
                      if second == ONSEC2:
               #         GPIO.output(LED1, GPIO.LOW)
                #        GPIO.output(LED2, GPIO.LOW)
                        GPIO.output(MARS, GPIO.LOW)
            
              if hour == OFFHOUR2:
                    if minute == OFFMIN2:
                      if second == OFFSEC2:
                 #       GPIO.output(LED1, GPIO.HIGH)
                  #      GPIO.output(LED2, GPIO.HIGH)
                        GPIO.output(MARS, GPIO.HIGH)                      
         
    
    else:
        
        time.sleep(0.2)
        
        print('System Failure')
        
GPIO.cleanup()

