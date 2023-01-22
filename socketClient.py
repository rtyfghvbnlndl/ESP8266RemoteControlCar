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
        
        
    def recv(self,timeout):
        print('wait reply...')
        self.cliSocket.settimeout(timeout)
        reply = self.cliSocket.recv(512).decode()
        print('server:'+self.reply)
        return reply
    #encrypt
    def sendE(self,message):
        self.cliSocket.send(message)
        print('client:encrypted message')
        
        
    def recvE(self,timeout):
        print('wait reply...')
        self.cliSocket.settimeout(timeout)
        reply = self.cliSocket.recv(512)
        print('server:encrypted message')
        return reply

    def close(self):
        self.cliSocket.close()




