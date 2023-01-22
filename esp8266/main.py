import st
import socketClient
import time
import network
from machine import PWM,Pin,ADC,I2C
import mpu6050

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
            
            led.value(0)
            print('try'+str(address))
            c1 = socketClient.client()
            try:c1.connect(address, 8266,3)
            except:continue
            print('ok')
            try:
                led.value(1)
                break
            except:pass
        else:
            continue
        isTimeout=False
        while not isTimeout:
            c1.send('51')
            try:
                header=eval(c1.recv(3))
                if header:break
            except:
                isTimeout=True
        else:continue
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
        continue
    config = header[6]
    if header[7]['mpu6050']:#是否启用mpu6050
        open6050 = True
        aNum = header[7]['mpu6050'][0]
        i2c = I2C(scl=Pin(12),sda=Pin(14))
        mpu = mpu6050.accel(i2c)
    adc = ADC(0)
    sleTime=0.05
    rl=None

    while True:#循环请求指令
        message={'sle':sleTime}#返回信息
        for n,item in enumerate(pwmN):
            message['duty%i'%n]=item.duty()
        message['adc']=adc.read()
        message['rl']=rl
        m=mpu.get_values()
        c1.send(message)
#上一次信息已经返回
        try:reply=eval(c1.recv(1))
        except:
            print('no reply')
            break
        
        if reply["config"]:
            config=reply["config"]
#方向无操作时自动控制方向 mpu6050
        if (not reply['duty1'])and open6050:
            if pwm0.duty()>config[0]['mid']:#判断前后
                a=-1#控制正负
            else:a=1
            
            numset=pwm1.duty()-int(m['GyZ']/aNum)*a
            if numset>config[1]['max']:
                numset=config[1]['max']
            elif numset<config[1]['min']:
                numset=config[1]['min']
            #右
            if  m['GyZ']<-500:
                reply['duty1']=numset
                rl='Left'
            #左
            elif m['GyZ']>500:
                reply['duty1']=numset
                rl="Right"
            else:
                rl=None
            print(m['GyZ'],rl,pwm1.duty())
#应用参数
        for n,item in enumerate(pwmN):
            if reply['duty%i'%n]:
                item.duty(reply['duty%i'%n])

        eval(reply['mes'])
    for item in pwmN:
        item.deinit()
    c1.send('"close"')
    c1.close()
    st.ledTwinkle([1,0.5],2)





























