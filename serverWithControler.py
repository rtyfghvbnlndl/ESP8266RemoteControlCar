import pygame
import time
from socketServer import server
from tools import fRead,fWrite

def toDuty(config,freq,per):#毫秒计算
    ma,mid,mi=config['ma'],config['mid'],config['mi']
    if per<0:
        tim=-(ma-mid)*per+mid
    elif per>0:
        tim=-(mid-mi)*per+mid
    else: tim=mid
    duty=tim*freq/1000
    duty=int(duty*1023)
    return duty

def perDuty(per):#占空比计算备用
    ma,mid,mi=10,5,0
    if per<0:
        duty=-(ma-mid)*per+mid
    elif per>0:
        duty=-(mid-mi)*per+mid
    else: duty=mid
    return duty

def moveAll(config,num):
    config['ma']+=num
    config['mid']+=num
    config['mi']+=num

def zoom(config,upOrDown):
    #config['ma'],config['mid'],config['mi']
    if upOrDown=='up' and config['ma']<2 and config['mi']>1:
        config['ma']+=0.01
        config['mi']-=0.01
    if upOrDown=='down' and config['ma']>1.5 and config['mi']<1.5:
        config['ma']-=0.01
        config['mi']+=0.01

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
if fRead('config'):
    config=fRead('config')
else:
    config=[{'ma':2,'mid':1.5,'mi':1},{'ma':2,'mid':1.5,'mi':1}]
print(config)

while True:
    #验证身份
    while True:
        s1 = server()
        s1.on(8266,6)
        if s1.recv()=='51':
            s1.send([51,{'pin':5,'freq':100},{'pin':4,'freq':100},{},{},{}])
            break
        s1.close()
    #初始化数据
    axis1,axis0=[0,0,0,0,0],[0,0,0,0]
    zeroNum=0
    lowBatErro=0
    #接收
    while True:
        try:message=eval(s1.recv())
        except:
            print('no message')
            continue
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
                zeroNum+=1
            else:
                axis0[i]=axis#记录上一次的值
                zeroNum=0
            axis1[i]=axis#摇杆表
        #获取按键动作
        button=[]
        for i in range(butNum):
            buis=joystick.get_button(i)
            button.append(buis)
        #油门偏移缩放
        if button[13]:
            if button[2]:moveAll(config[0],0.02)
            if button[1]:moveAll(config[0],-0.02)
            if button[0]:zoom(config[0],'up')
            if button[3]:zoom(config[0],'down')
        if button[14]:
            if button[2]:moveAll(config[1],0.02)
            if button[1]:moveAll(config[1],-0.02)
            if button[0]:zoom(config[1],'up')
            if button[3]:zoom(config[1],'down')
        #处理结果
        if message['adc'] and zeroNum>3:#低电压保护
            if volt(message['adc'])<=6.4:
                lowBatErro+=1
            else:
                if lowBatErro>0:
                    lowBatErro-=1
            if lowBatErro>4:
                #reply['mes']='close'
                print('LOW BATTERY! RECHARGE!')
                #break
        if button[10]:
            axis1[3]=-1
            zeroNum=0
        if button[9]:
            axis1[1]=-1
            zeroNum=0
        reply={'duty0':round(toDuty(config[0],100,axis1[1]),3),'duty1':round(toDuty(config[1],100,axis1[3]),3),'sle':None,'mes':None}
        if zeroNum>250 or button[5]:
            reply['mes']='close'
        elif zeroNum>200:
            reply['sle']=5
        else:
             reply['sle']=0.05
        #压力测试
        #reply['sle']=0.001
        #if a:
        #    reply['duty']=[306,306]
        #else:
        #    reply['duty']=[206,206]
        #a=not a
        #zeroNum=3
        #删掉重复指令
        for key in ('duty0','duty1','sle'):
            if message[key]==reply[key]:
                reply[key]=None
        if button[15]:
            reply['duty0']=0
            reply['duty1']=0
        #发送结果
        apo=float(axis1[4])
        axis1[4]=time.time()
        #print('estimated delay:'+str((axis1[4]-apo)/2))
        s1.send(reply)
        #判断结束
        