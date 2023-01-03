import socket
import time

class server(object):
    def __init__(self):
        pass

    def on(self,port):
        self.serSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.serSocket.bind((socket.gethostname(),port))
        self.serSocket.listen(10)
        print('server on /n wait connect...')
        self.connect, self.address = self.serSocket.accept()
        print(str(self.address)+'connected')
        return self.address

    def recv(self):
        print('wait client...')
        self.message = self.connect.recv(1536).decode()
        print('[client]:'+self.message)
        return self.message
    
    def send(self,message):
        self.connect.send(str(message).encode())
        print('[server] reply:'+str(message))

    def close(self):
        self.connect.close()


if __name__=='__main__':
    while True:
        #验证身份
        while True:
            s1 = server()
            s1.on(8266)
            if s1.recv()=='01':
                s1.send('OK')
                break
            s1.close()
        #接收
        while True:
            message=s1.recv()
            match message:
                case 'close':
                    s1.send('closed')
                    s1.close()
                    break
                case _:
                    reply=str(time.time())
                    s1.send(reply)
    

