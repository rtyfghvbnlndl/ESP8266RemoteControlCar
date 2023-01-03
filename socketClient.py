import socket

class client(object):
    def __init__(self,host,port):
        self.host=host
        self.port=port

    def connect(self):
        self.cliSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.cliSocket.connect((self.host,self.port))

    def send(self,message):
        self.cliSocket.send(message.encode())
        print('send:'+str(message))
        print('wait reply...')
        self.reply = self.cliSocket.recv(512).decode()
        print('server:'+self.reply)
        return self.reply
    
    def close(self):
        self.cliSocket.close()

if __name__=='__main__':
    from time import sleep
    from datetime import datetime
    #验证身份
    while True:
        c1 = client(socket.gethostname(),8266)
        c1.connect()
        if c1.send(input('passwd:'))=='OK':
            break
        c1.close()
    while True:
        message=str(datetime.now())
        reply=c1.send(message)
        sleep(1)
        



