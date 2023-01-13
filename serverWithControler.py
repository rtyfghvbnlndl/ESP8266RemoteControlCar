import pygame
import time
from socketServer import server
from tools import fRead,fWrite

#新的控制器，按姿态控制
def toDuty(config,per):
    ma,mid,mi=config['max'],config['mid'],config['min']
    if per<0:
        duty=-(ma-mid)*per+mid
    elif per>0:
        duty=-(mid-mi)*per+mid
    else: duty=mid
    return duty

def volt(num):#算电池电压
    U0=3.3*num/1023
    U=U0*4
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
    config=[{'max':100,'mid':150,'min':200},{'max':100,'mid':150,'min':200}]
configed=list(config)
def bOrs(config):
    if config['max']<config['min']:
        ma=config['max']
        config['max']=config['min']
        config['min']=ma
    return config
for i in range(len(configed)):
    configed[i]=bOrs(configed[i])
print(config,configed)

while True:
    #验证身份
    while True:
        s1 = server()
        s1.on(8266,6)
        if s1.recv()=='51':
            s1.send([51,{'pin':5,'freq':100},{'pin':4,'freq':100},{},{},{},configed])
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
            if button[2]:config[0]['mid']+=1
            if button[1]:config[0]['mid']-=1
        if button[11]:
            if button[2]:config[0]['max']+=1
            if button[1]:config[0]['max']-=1
            if button[0]:config[0]['min']+=1
            if button[3]:config[0]['min']-=1
        if button[14]:
            if button[2]:config[1]['mid']+=1
            if button[1]:config[1]['mid']-=1
        if button[12]:
            if button[2]:config[1]['max']+=1
            if button[1]:config[1]['max']-=1
            if button[0]:config[1]['min']+=1
            if button[3]:config[1]['min']-=1
        #处理结果
        if message['adc'] and zeroNum>3:#低电压保护
            if volt(message['adc'])<=6.4:
                lowBatErro+=1
            else:
                if lowBatErro>0:
                    lowBatErro-=1
            if lowBatErro>4:
                reply['mes']='close'
                print('LOW BATTERY! RECHARGE!')
                break
        #一键满速
        if button[10]:
            axis1[3]=-1
            zeroNum=0
        if button[9]:
            axis1[1]=-1
            zeroNum=0
       
        #左摇杆纵向控制前后
        reply={'duty0':round(toDuty(config[0],axis1[1]),3),'duty1':round(toDuty(config[1],axis1[1]),3),'sle':None,'mes':None}
         #右摇杆横向控制转向
        half=abs(axis1[3])
        if axis1[3]!=0:
            if axis1[3]>0:#右
                reply['duty0']+=half*abs(config[0]['max']-config[0]['min'])
                if reply['duty0']>max(config[0]['max'],config[0]['min']):
                    reply['duty1']-=abs(config[1]['max']-config[1]['min'])*(abs(axis1[3])-(max(config[0]['max'],config[0]['min'])-reply['duty0'])/abs(config[0]['max']-config[0]['min']))
                    reply['duty0']=max(config[0]['max'],config[0]['min'])
                else:
                    reply['duty1']-=half*abs(config[1]['max']-config[1]['min'])
            else:#左
                reply['duty0']-=half*abs(config[0]['max']-config[0]['min'])
                if reply['duty0']<min(config[0]['max'],config[0]['min']):
                    reply['duty1']+=abs(config[1]['max']-config[1]['min'])*(abs(axis1[3])-(reply['duty0']-min(config[0]['max'],config[0]['min']))/abs(config[0]['max']-config[0]['min']))
                    reply['duty0']=min(config[0]['max'],config[0]['min'])
                else:
                    reply['duty1']+=half*abs(config[1]['max']-config[1]['min'])

        #无操作休眠
        if zeroNum>1100 or button[5]:
            reply['mes']='close'
        elif zeroNum>1000:
            reply['sle']=5
        else:
             reply['sle']=0.01
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
        