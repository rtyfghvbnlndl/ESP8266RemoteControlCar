import socket

class client(object):
    def __init__(self,host,port):
        self.host=host
        self.port=port

    def connect(self):
        self.cliSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        address=socket.getaddrinfo(self.host, self.port)[0][-1]
        self.cliSocket.connect(address)

    def send(self,message):
        self.cliSocket.send(str(message).encode())
        print('[client] send:'+str(message))
        print('wait reply...')
        self.reply = self.cliSocket.recv(1536).decode()
        print('[server]:'+self.reply)
        return self.reply
    
    def close(self):
        self.cliSocket.close()
    
    def noReplySend(self,message):
        self.cliSocket.send(str(message).encode())
        print('[client] no reply send:'+str(message))

if __name__=='__main__':
 
    while True:
        c1 = client('192.168.10.24',8266)
        c1.connect()
        if c1.send('01')=='OK':
            break
        c1.close()
    while True:
        message='1234'
        reply=c1.send(message)




