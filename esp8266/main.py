import st
import socketClient
import time
import network
from machine import PWM,Pin

wlan=None
def do_connect(ssid1, key1):#连接wifi函数
    global wlan
    wlan = network.WLAN(network.STA_IF)
    print(type(wlan))
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(ssid1, key1)
        for i in range(30):
            time.sleep(0.5)
        if wlan.isconnected():
            print('network config:', wlan.ifconfig())
        else:
            print('timeout')
            st.ledTwinkle([0.5, 1], 10)

st.ledTwinkle([1, 0.5], 2)
do_connect('Router', 'setup0000')
addressList=['192.168.10.24','192.168.10.112']
while not wlan.isconnected():#确认wifi连接
    pass
else:
    while True:#验证身份
        st.ledTwinkle([0.5], 2)
        for address in addressList:
            try:
                c1 = socketClient.client(address, 8266)
                c1.connect()
                break
            except:pass
        if c1.send('01')=='OK':
            break
        c1.close()
    pwm0 = PWM (Pin(0), freq=50, duty=0)
    pwm1 = PWM (Pin(4), freq=50, duty=0)
    led = Pin(2, mode=Pin.OUT, pull=Pin.PULL_UP, value=1)
    sleTime=0.05
    while True:#循环请求指令
        message={'sle':sleTime}
        try:reply=eval(c1.send(message))
        except:#失联处理
            pwm0.duty(0)
            pwm1.duty(0)
            for i in range(5):
                c1.noReplySend('01')
                time.sleep(1)
            continue
        if reply['freq']:#填入接收的信息
            pwm0.freq(reply['freq'][0])
            pwm1.freq(reply['freq'][1])
        if reply['duty']:
            pwm0.duty(reply['duty'][0])
            pwm1.duty(reply['duty'][1])
        if reply['sle']:
            sleTime=reply['sle']
        time.sleep(sleTime)
        if reply['mes']=='close':#收到关闭指令
            break
    pwm0.deinit()
    pwm1.deinit()
    c1.send('close')
    c1.close()
    st.ledTwinkle([1,0.5],2)






