from machine import Pin
from time import sleep
import network


def ledTwinkle(list,num):
    led = Pin(2, Pin.OUT)
    for i in range(num):
        for time in list:
            led.value(0)
            sleep(time/2) 
            led.value(1)
            sleep(time/2)
if __name__=='__main__':
    ledTwinkle([0.2,0.3],2)
    if [] :
        print(12)

  





