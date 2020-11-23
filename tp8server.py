import socket
import psutil
import platform
import cpuinfo
import pickle
import time
import os
from datetime import datetime
# Cria o socket
socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Obtém o nome da máquina
# host = socket.gethostname()
host = '192.168.100.7'
porta = 9999
# Associa a porta
socket_servidor.bind((host, porta))
# Escutando...
socket_servidor.listen()

sistema = platform.system()

print("Servidor de nome", host, "esperando conexão na porta", porta)

processador='Processador: '
rede=''
array=0 
sistema = platform.system()
info = cpuinfo.get_cpu_info()
rede=''
processador=''
if sistema == 'Linux':
    rede='wlp3s0'
    processador += info['brand_raw']
elif sistema == 'Windows':
    rede='Wi-Fi'
    array=1
    processador += platform.processor()
elif sistema == 'Darwin':
    processador += info['brand_raw']
    rede='en0'

#CPU
cpus_count=psutil.cpu_count()
arquitetura = 'Arquitetura: '  + info['arch']
nome= processador
bits='Palavra: '+str(info['bits']) + ' Bits'
cpuscount='Núcleos (Logicos):'+str(cpus_count)
cpuscountfisical='Nucleos (Fisicos):'+str(psutil.cpu_count(logical=False))
frequencia_total='Frequencia total: '+str(round(psutil.cpu_freq().max,2)) +' MHz'

def get_monitoramento():
    def inGB(m):
        if m is not None:
            return str(round(m/(1024*1024*1024),2))

    frequencia='Frequencia: '+ str(round(psutil.cpu_freq().current,2)) + ' MHz'

    #Memoria
    mem = psutil.virtual_memory()
    memoria_total="Memoria Total:"+ inGB(mem.total)+ " GB"
    memoria_disponivel="Memoria Disponivel:"+ inGB(mem.available)+ " GB"
    memoria_livre="Memoria Livre:"+ inGB(mem.free)+ " GB"
    memoria_usada="Memoria Usada:"+ inGB(mem.used)+ " GB"

    net= psutil.net_if_addrs()[rede][0]
    nets=[]

    for i in psutil.net_if_addrs():
        for x in psutil.net_if_addrs()[i]:
            if '192.' in x.address:
                ip= 'IP: '+ str(net.address)
                if ip not in nets:
                    netmask='NetMask: '+ str(net.netmask)
                    family='Family: ' + str(net.family)
                    ptp='Ptp: '+str(net.ptp)
                    nets=nets+[ip,netmask,family,ptp]
    memoria_os=[]
    net_os=[]
    if sistema == 'Linux':
        memoria_buffers="Buffers:"+ inGB(mem.buffers)+ " GB"
        memoria_cached="Cached:"+ inGB(mem.cached)+ " GB"
        memoria_shared="Compartilhada:"+  inGB(mem.shared)+ " GB"
        memoria_slab="Slab:"+ inGB(mem.slab)+ " GB"
        memoria_ativa="Memoria Ativa:"+ inGB(mem.active)+ " GB"
        memoria_inativa="Memoria Inativa:"+ inGB(mem.inactive)+ " GB"
        memoria_os=[memoria_buffers,memoria_cached,memoria_shared,memoria_slab,memoria_ativa,memoria_inativa]
        net_os=['BroadCast: '+net.broadcast]
    elif sistema == 'Windows':
        print("nenhum extra no windows")
    elif sistema == 'Darwin':
        memoria_ativa="Memoria Ativa:"+ inGB(mem.active) + " GB"
        memoria_inativa="Memoria Inativa:"+ inGB(mem.inactive) + " GB"
        memoria_wired="Wired: "+inGB(mem.wired)+ " GB"
        memoria_os=[memoria_ativa,memoria_inativa,memoria_wired]
        net_os=['BroadCast: '+ str(net.broadcast)]

    disco= psutil.disk_usage('.')
    disco_total='Disco Total: '+ inGB(disco.total) +' GB'
    disco_usado='Disco Usado: '+ inGB(disco.used)+' GB'
    disco_livre='Disco Livre: '+ inGB(disco.free)+' GB'



    processador_info=['Processador:',nome,arquitetura,frequencia_total,frequencia,bits,cpuscount,cpuscountfisical]
    memoria_info=['Memoria: ', memoria_total,memoria_disponivel,memoria_usada,memoria_livre]+memoria_os
    disco_info=['Disco:',disco_total,disco_usado,disco_livre]
    net_info=['Rede:']+nets+net_os
    resumo_info=['Resumo: ',nome,cpuscount,memoria_total,memoria_disponivel,memoria_usada,memoria_livre,disco_total,disco_usado,disco_livre,ip,netmask]


    infos=[processador_info,memoria_info,disco_info,net_info,resumo_info]


    pct_memoria = psutil.virtual_memory().percent
    pct_cpu = psutil.cpu_percent()
    pct_disco = psutil.disk_usage('.').percent

    CPUS=psutil.cpu_percent(percpu=True)

    resp = dict()
    resp['pct_memoria'] = pct_memoria
    resp['pct_cpu'] = pct_cpu
    resp['pct_disco'] = pct_disco
    resp['infos'] = infos
    resp['CPUS'] = CPUS
    
    return resp

qtd_processos=0
page_size=20
def get_processos(page):
    global qtd_processos
    def pegar_info(pid):
        try:
            p = psutil.Process(pid)
            texto = '{:^7}'.format(pid)
            texto = texto + '{:^11}'.format(p.num_threads())
            texto = texto + " " + time.ctime(p.create_time()) + " "
            texto = texto + '{:8.2f}'.format(p.cpu_times().user)
            texto = texto + '{:8.2f}'.format(p.cpu_times().system)
            texto = texto + '{:10.2f}'.format(p.memory_percent()) + " MB"
            rss = p.memory_info().rss/1024/1024
            texto = texto + '{:10.2f}'.format(rss) + " MB"
            vms = p.memory_info().vms/1024/1024
            texto = texto + '{:10.2f}'.format(vms) + " MB"
            texto = texto + " " + p.exe()
            return texto
        except:
            pass  
    lista = psutil.pids()
    aux=0
    auxidx=0
    pages=[]
    for pid in lista:
        info_process = pegar_info(pid)
        if info_process != None:
            if aux==0 and auxidx==0:
                pages.append([])
            
            if auxidx < page_size:
                pages[aux].append(info_process)
            else:
                auxidx=0
                aux=aux+1
                pages.append([])
                pages[aux].append(info_process)
            auxidx=auxidx+1
    
    resp = dict()
    if page >= len(pages):
        return {}

    resp['pagina']=pages[page]
    resp['max']=len(pages)-1

    return resp


def get_diretorios():
    directs = os.listdir('./')
    diretorios = dict()
    totArquivos=0
    totBytes=0
    lista = []
    t="|{:35}|{:>10}|{:21}|{:21}|"
    lista.append(t.format("Name","Size","Criado em","Modificado em"))
    
    for name in directs:
        namePath = './'+name

        dtatime = datetime.fromtimestamp(os.stat(namePath).st_atime)

        formatdtatime = ("{:{dfmt} {tfmt}}".format(dtatime, dfmt="%d-%m-%Y", tfmt="%H:%M"))
        dtmtime = datetime.fromtimestamp(os.stat(namePath).st_mtime)
        formatdtmtime = ("{:{dfmt} {tfmt}}".format(dtmtime, dfmt="%d-%m-%Y", tfmt="%H:%M"))

        text = t.format(name,str(os.stat(namePath).st_size/1000),formatdtatime,formatdtmtime)
        lista.append(text)
       
        totArquivos +=1
        totBytes = totBytes + os.stat(namePath).st_size

    diretorios['lista'] = lista
    diretorios['total'] = totArquivos
    diretorios['bytes_total'] = totBytes
    return diretorios

while True:
    # Aceita alguma conexão
    (socket_cliente,addr) = socket_servidor.accept()	
    print("Conectado a:", str(addr))
    resposta = ''
    msg = socket_cliente.recv(1024)
    # Decodifica mensagem em ASCII
    msg = pickle.loads(msg)
    print('Tipo requisicao:',msg['name'])
    if msg['name'] == 'monitoramento': 
        resposta = pickle.dumps(get_monitoramento())
    if msg['name'] == 'processos':
        resposta = pickle.dumps(get_processos(msg['payload']))
    if msg['name'] == 'diretorios':
        resposta = pickle.dumps(get_diretorios())
    socket_cliente.send(resposta)
    socket_cliente.close()