from Crypto.Cipher import AES

class aes(object):

    def __init__(self, passwd):
        self.aes = AES.new(passwd, AES.MODE_ECB)

    def en(self, text):
        text=text.encode()
        while len(text)%16 != 0:
            text += b" "
        enText = self.aes.encrypt(text)
        return enText

    def de(self, text):
        deText = self.aes.decrypt(text)
        return deText.decode().rstrip(" ")

if __name__ == "__main__":
    aes1 = aes(b"dhsuehdyfgyehduf")
    
    a=aes1.en("adajskdka")#in:<class 'str'>
    print(a,type(a))#out:<class 'bytes'>

    b=aes1.de(a.encode())#in:<class 'bytes'>
    print(b,type(b))#out:<class 'str'>