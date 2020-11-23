import socket,time,pickle

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

# host = socket.gethostname()
host = '192.168.100.7'
s.connect((host,9999))

def request(message):
    try:
        message = pickle.dumps(message)
        s.send(message)
        data = s.recv(4096)
        return pickle.loads(data)
    except Exception as erro:
        print(str(erro))



resposta = request({'name':'processos','payload':2})
# resposta = request({'name':'monitoramento'})
print(resposta)
print('closing')
s.close()