import socket
import time

class server(object):
    def __init__(self):

        pass

    def on(self,port):
        self.serSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.serSocket.bind((socket.gethostname(),port))
        self.serSocket.listen(10)
        print('server on')

    def connect(self):
        print("wait connect")
        self.connec, self.address = self.serSocket.accept()
        print(str(self.address)+'connected')
        return self.address

    def recv(self,timeout):
        print('wait client...')
        self.connec.settimeout(timeout)
        message = self.connec.recv(1536).decode()
        print('[client]:'+message)
        return message
    
    def send(self,message):
        self.connec.send(str(message).encode())
        print('[server] reply:'+str(message))

    def close(self):
        self.connec.close()


