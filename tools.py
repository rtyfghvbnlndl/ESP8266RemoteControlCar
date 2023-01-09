from contextlib import closing
import requests
import os
from time import sleep
from random import randint


#统计成功率
class counter(object):
    def __init__(self,adict,num):
        self.adict=adict
        self.num=num
    def fail(self,anyKey):
        if self.num:print("[X]%s失败"%anyKey)
        if not anyKey in self.adict.keys():self.adict[anyKey]={'f':1,'s':0}
        else:self.adict[anyKey]['f']+=1
    def success(self,anyKey):
        if self.num:print("[O]%s成功"%anyKey)
        if not anyKey in self.adict.keys():self.adict[anyKey]={'f':0,'s':1}
        else:self.adict[anyKey]['s']+=1
    def show(self):
        r=''
        for keys in self.adict:
            f=self.adict[keys]['f']
            s=self.adict[keys]['s']
            r+='|%s %i/%i failRate:%.2f%%| '%(keys,f,s+f,f/(s+f)*100)
        print(r)
    #带统计功能的savePic
    def savePic(self,url,name,h):
        d="./pic/"
        ext=getExt(url,['Webp','BMP','GIF','JPEG','jpg','SVG','PNG','ICO'])
        if url and name:
            if not os.path.exists(d):
                os.mkdir(d)
            try:
                sleep(randint(3,70)/100)
                r=requests.get("http://"+str(url),headers=h)
                with closing(r) as response:
                    with open('%s%s.%s' % (d,str(name),ext), 'wb') as fd:
                        for chunk in response.iter_content(128):
                            fd.write(chunk)
                self.success("pic")
            except:
                self.fail('pic')

#找扩展名
def getExt(url,alist):
    for ext in alist:
        ext=ext.lower()
        if url.lower()[-len(ext):]==ext:
            return ext
    return 'jpg'

#保存图片
def savePic(url,name,h):
    d="./pic/"
    ext=getExt(url,['Webp','BMP','GIF','JPEG','jpg','SVG','PNG','ICO'])
    if url and name:
        if not os.path.exists(d):
            os.mkdir(d)
        try:
            sleep(randint(3,70)/100)
            r=requests.get("http://"+str(url),headers=h)
            with closing(r) as response:
                with open('%s%s.%s' % (d,str(name),ext), 'wb') as fd:
                    for chunk in response.iter_content(128):
                        fd.write(chunk)
            print(str(name)+"成功")
        except:
            print(str(name)+"失败")

#存档
def fWrite(content,name):
    with open("%s\%s.txt" % (os.path.dirname(__file__),name),"w+",encoding="utf-8",newline="") as f:
        f.write(str(content))
        print('写入成功')

#读档
def fRead(name):
    if not os.path.exists("%s\%s.txt" % (os.path.dirname(__file__),name)):
        return None
    with open("%s\%s.txt" % (os.path.dirname(__file__),name),"r",encoding="utf-8",newline="") as f:
        content=f.read()
        return eval(content)


if __name__=="__main__":
    if fRead('config'):
        config=fRead('config')
    else:
        config=[{'ma':2,'mid':1.5,'mi':1},{'ma':2,'mid':1.5,'mi':1}]
    print(config)