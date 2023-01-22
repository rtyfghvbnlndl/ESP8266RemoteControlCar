import pygame
import time
from socketServer import server
from tools import fRead,fWrite

def toDuty(config,per):
    ma,mid,mi=config['max'],config['mid'],config['min']
    if per<0:
        duty=-(ma-mid)*per+mid
    elif per>0:
        duty=-(mid-mi)*per+mid
    else: duty=mid
    return int(duty)
def volt(num):#算电池电压
    U0=3.3*num/1023
    U=U0*3
    return U

pygame.init()
pygame.joystick.init()
while True:
    pygame.event.get()
    try:
        joystick = pygame.joystick.Joystick(0)
        break
    except:
        input("wait gamecontoler...input something")
        continue
#为了能看到配置
def rcon():
    if fRead('config'):
        config=fRead('config')
    else:
        config=[{'max':220,'mid':160,'min':100},{'max':220,'mid':160,'min':100}]
    return config
config=rcon()
configed=list(config)
def bOrs(config0):
    config=dict(config0)
    if config['max']<config['min']:
        ma=config['max']
        config['max']=config['min']
        config['min']=ma
    return config
for i in range(len(configed)):
    configed[i]=bOrs(configed[i])
print(config,configed)


s1 = server()
s1.on(8266)
while True:
    #验证身份
    while True: 
        fWrite(config,'config')
        s1.connect()
       
        reply=s1.recv(10)
        try:
            if reply=='51':
                s1.send([51,{'pin':5,'freq':100},{'pin':4,'freq':100},{},{},{},configed,{'mpu6050':[1000]}])
                break
        except:pass
        s1.close()
    #初始化数据
    axis1,axis0=[0,0,0,0,0],[0,0,0,0]
    zeroNum=[0,0,0,0]
    lowBatErro=0
    change=False
    #接收
    while True:
        try:message=eval(s1.recv(1))
        except:
            s1.close()
            break
        if message=='close' or message=='51':
                s1.send('closed')
                s1.close()
                fWrite(config,'config')
                break
        #获取摇杆动作
        pygame.event.get()
        joystick = pygame.joystick.Joystick(0)
        butNum=joystick.get_numbuttons()
        for i in range(4):
            axis = joystick.get_axis(i)
            if (abs(axis)<0.5 and abs(axis-axis0[i])<0.005) or abs(axis)<0.06:#过滤遥杆偏移
                axis=0
                zeroNum[i]+=1
            else:
                axis0[i]=axis#记录上一次的值
                zeroNum[i]=0
            axis1[i]=axis#摇杆表
        #获取按键动作
        button=[]
        for i in range(butNum):
            buis=joystick.get_button(i)
            button.append(buis)
        #油门偏移缩放
        if button[13]:
            change=True
            if button[2]:config[0]['mid']+=1
            if button[1]:config[0]['mid']-=1
        if button[11]:
            change=True
            if button[2]:config[0]['max']+=1
            if button[1]:config[0]['max']-=1
            if button[0]:config[0]['min']+=1
            if button[3]:config[0]['min']-=1
        if button[14]:
            change=True
            if button[2]:config[1]['mid']+=1
            if button[1]:config[1]['mid']-=1
        if button[12]:
            change=True
            if button[2]:config[1]['max']+=1
            if button[1]:config[1]['max']-=1
            if button[0]:config[1]['min']+=1
            if button[3]:config[1]['min']-=1
        print( volt(message['adc']))
        if message['adc'] and zeroNum[1]>3 and zeroNum[2]>3:#低电压保护
            if volt(message['adc'])<=6.4:
                print( volt(message['adc']))
                lowBatErro+=1
            else:
                if lowBatErro>0:
                    lowBatErro-=1
            if lowBatErro>4:
                #reply['mes']='break'
                print('LOW BATTERY! RECHARGE!')
                print(volt(message['adc']))
        if button[10]:
            axis1[2]=-1
            zeroNum[2]=0
        if button[9]:
            axis1[1]=-1
            zeroNum[1]=0
        reply={'duty0':toDuty(config[0],axis1[1]),'duty1':toDuty(config[1],axis1[2]),'config':None,'mes':None}#本次reply
        if button[5]:
            reply['mes']='break'
        elif zeroNum[1]>500 and zeroNum[2]>500:
            reply['mes']='time.sleep(1)'
        else:
            reply['mes']='time.sleep(0.01)'
        if change==True:
            reply['config']=config
            change=False
        #无动作返回None
        if zeroNum[2]>4:
            reply['duty1']=None
        if zeroNum[1]>4:
            reply['duty0']=None

        #发送结果
        
        apo=float(axis1[4])
        axis1[4]=time.time()
        #print('estimated delay:'+str((axis1[4]-apo)/2))
        s1.send(reply) 
        