import socket,time

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

s.connect(('192.168.100.7',9999))

def sendmessage(message):
    try:
        s.send(message.encode('utf-8'))
        data = s.recv(1024)
        return data.decode('utf-8')
    except Exception as erro:
        print(str(erro))


resposta = sendmessage('Ola servidor') 

print(resposta)
print('closing')
s.close()