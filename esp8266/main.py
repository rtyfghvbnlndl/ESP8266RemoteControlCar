import st
import socketClient
import time
import network
from machine import PWM,Pin,ADC

st.ledTwinkle([0.5,1], 2)#开机闪led
led=Pin(2, Pin.OUT)

def do_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('Router', 'setup0000')
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())
    return wlan

addressList=['192.168.10.24','192.168.10.112']

while not do_connect().isconnected():#确认wifi连接
    do_connect()

while True:
    while True:#握手
        st.ledTwinkle([0.5], 2)
        for address in addressList:
            try:
                led.value(0)
                print('try'+str(address))
                c1 = socketClient.client()
                c1.connect(address, 8266,0.5)
                print('ok')
                led.value(1)
                break
            except:pass
        else:
            continue
        while True:
            c1.send('51')
            header=eval(c1.recv())
            if header:break
        pwmN=[]
        if header[0]==51:
            if header[1]:
                pwm0 = PWM (Pin(header[1]['pin']), freq=header[1]['freq'], duty=0)
                pwmN.append(pwm0)
            if header[2]:
                pwm1 = PWM (Pin(header[2]['pin']), freq=header[2]['freq'], duty=0)
                pwmN.append(pwm1)
            if header[3]:
                pwm2 = PWM (Pin(header[3]['pin']), freq=header[3]['freq'], duty=0)
                pwmN.append(pwm2)
            if header[4]:
                pwm3 = PWM (Pin(header[4]['pin']), freq=header[4]['freq'], duty=0)
                pwmN.append(pwm3)
            if header[5]:
                pwm4 = PWM (Pin(header[5]['pin']), freq=header[5]['freq'], duty=0)
                pwmN.append(pwm4)
            break
        c1.close()
    adc = ADC(0)
    sleTime=0.05

    while True:#循环请求指令
        message={'sle':sleTime}#返回信息
        for n,item in enumerate(pwmN):
            message['duty%i'%n]=item.duty()
        message['adc']=adc.read()
        c1.send(message)
        try:reply=eval(c1.recv())
        except:
            for item in pwmN:
                item.duty(0)
            print('no reply')
            c1.close()
            break
        for n,item in enumerate(pwmN):
            if reply['duty%i'%n]:
                item.duty(reply['duty%i'%n])
        if reply['sle']:
            sleTime=reply['sle']
        time.sleep(sleTime)
        if reply['mes']=='close':#收到关闭指令
            for item in pwmN:
                item.deinit()
            c1.send('"close"')
            c1.close()
            st.ledTwinkle([1,0.5],2)




























