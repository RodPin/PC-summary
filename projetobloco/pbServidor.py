import socket
import psutil
import platform
import cpuinfo
import pickle
import time
import os
from datetime import datetime
from threading import Thread
import nmap
import subprocess

# Cria o socket
socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Obtém o nome da máquina
host = socket.gethostname()

porta = 9999
# Associa a porta
socket_servidor.bind((host, porta))
# Escutando...
socket_servidor.listen()

sistema = platform.system()

print("Servidor de nome", host, "esperando conexão na porta", porta)

interface_rede_atual= ['',0]
redes_infos = psutil.net_io_counters(pernic=True)
for info_rede in redes_infos:
    bytes_env=redes_infos[info_rede].bytes_sent
    if interface_rede_atual[1] < bytes_env:
        interface_rede_atual[0] =info_rede
        interface_rede_atual[1]= bytes_env

processador='Processador: '
array=0 
sistema = platform.system()
info = cpuinfo.get_cpu_info()
processador=''
if sistema == 'Linux':
    processador += info['brand_raw']
elif sistema == 'Windows':
    array=1
    processador += platform.processor()
elif sistema == 'Darwin':
    processador += info['brand_raw']

#CPU
cpus_count=psutil.cpu_count()
arquitetura = 'Arquitetura: '  + info['arch']
nome= processador
bits='Palavra: '+str(info['bits']) + ' Bits'
cpuscount='Núcleos (Logicos): '+str(cpus_count)
cpuscountfisical='Nucleos (Fisicos): '+str(psutil.cpu_count(logical=False))
frequencia_total='Frequencia total: '+str(round(psutil.cpu_freq().max,2)) +' MHz'

CPUS=''
count=0
def get_monitoramento():
    global CPUS,count
    def inGB(m):
        if m is not None:
            return str(round(m/(1024*1024*1024),2))

    frequencia='Frequencia: '+ str(round(psutil.cpu_freq().current,2)) + ' MHz'

    #Memoria
    mem = psutil.virtual_memory()
    memoria_total="Memoria Total: "+ inGB(mem.total)+ " GB"
    memoria_disponivel="Memoria Disponivel: "+ inGB(mem.available)+ " GB"
    memoria_livre="Memoria Livre: "+ inGB(mem.free)+ " GB"
    memoria_usada="Memoria Usada: "+ inGB(mem.used)+ " GB"

    net= psutil.net_if_addrs()[interface_rede_atual[0]][0]
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
        memoria_buffers="Buffers: "+ inGB(mem.buffers)+ " GB"
        memoria_cached="Cached: "+ inGB(mem.cached)+ " GB"
        memoria_shared="Compartilhada: "+  inGB(mem.shared)+ " GB"
        memoria_slab="Slab: "+ inGB(mem.slab)+ " GB"
        memoria_ativa="Memoria Ativa: "+ inGB(mem.active)+ " GB"
        memoria_inativa="Memoria Inativa: "+ inGB(mem.inactive)+ " GB"
        memoria_os=[memoria_buffers,memoria_cached,memoria_shared,memoria_slab,memoria_ativa,memoria_inativa]
        net_os=['BroadCast: '+str(net.broadcast)]
    elif sistema == 'Windows':
        print("nenhum extra no windows")
    elif sistema == 'Darwin':
        memoria_ativa="Memoria Ativa: "+ inGB(mem.active) + " GB"
        memoria_inativa="Memoria Inativa: "+ inGB(mem.inactive) + " GB"
        memoria_wired="Wired: "+inGB(mem.wired)+ " GB"
        memoria_os=[memoria_ativa,memoria_inativa,memoria_wired]
        net_os=['BroadCast: '+ str(net.broadcast)]

    disco= psutil.disk_usage('.')
    disco_total='Disco Total: '+ inGB(disco.total) +' GB'
    disco_usado='Disco Usado: '+ inGB(disco.used)+' GB'
    disco_livre='Disco Livre: '+ inGB(disco.free)+' GB'



    processador_info=['Processador:',nome,arquitetura,frequencia_total,frequencia,bits,cpuscount,cpuscountfisical]
    memoria_info=['Memoria: ', memoria_total,memoria_disponivel,memoria_usada,memoria_livre]+memoria_os
    disco_info=['Disco: ',disco_total,disco_usado,disco_livre]
    net_info=['Rede: ']+nets+net_os
    resumo_info=['Resumo: ',nome,cpuscount,memoria_total,memoria_disponivel,memoria_usada,memoria_livre,disco_total,disco_usado,disco_livre,ip,netmask]


    infos=[processador_info,memoria_info,disco_info,net_info,resumo_info]


    pct_memoria = psutil.virtual_memory().percent
    pct_cpu = psutil.cpu_percent()
    pct_disco = psutil.disk_usage('.').percent

    if count == 0:
        CPUS=psutil.cpu_percent(percpu=True)
    count=count+1
    if count == 4:
        count=0

    resp = dict()
    resp['pct_memoria'] = pct_memoria
    resp['pct_cpu'] = pct_cpu
    resp['pct_disco'] = pct_disco
    resp['infos'] = infos
    resp['CPUS'] = CPUS
    resp['disco'] = disco
    
    return resp

page_size=20
def get_processos(page):
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
    resp['qtd']=len(lista)

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

def get_trafego_rede():
    redes_infos = psutil.net_io_counters(pernic=True)
    t2="|{:^20}|{:^20}|{:^20}|{:^20}|{:^20}|"
    textos_rede_info=[]        
    textos_rede_info.append(t2.format('Interface','Bytes enviados','Bytes Recebidos','Pacotes enviados','Pacotes recebidos'))
    for info_rede in redes_infos:
        ri_dic=redes_infos[info_rede]
        label = t2.format(info_rede,ri_dic.bytes_sent,ri_dic.bytes_recv,ri_dic.packets_sent,ri_dic.packets_recv)
        textos_rede_info.append(label)
    return textos_rede_info  

def retorna_codigo_ping(hostname):
    plataforma = platform.system()
    args = []
    if plataforma == "Windows":
        args = ["ping", "-n", "1", "-l", "1", "-w", "100", hostname]

    else:
        args = ['ping', '-c', '1', '-W', '1', hostname]
        
    ret_cod = subprocess.call(args,stdout=open(os.devnull, 'w'),stderr=open(os.devnull, 'w'))
    return ret_cod

def get_host():
    global interface_rede_atual
    aux = psutil.net_if_addrs()[interface_rede_atual[0]][array].address.split('.')
    aux.pop()
    return '.'.join(aux)+'.'
def verifica_hosts(base_ip=get_host()):
    host_validos = []
    return_codes = dict()
    for i in range(1,255):
        host_editado = base_ip + '{0}'.format(i)
        return_codes[host_editado] = retorna_codigo_ping(host_editado)
        if i %20 ==0:
            print(".", end = "")
        if return_codes[host_editado] == 0:
            host_validos.append(host_editado)

    return host_validos

def adiciona_info_portas(nm,host,info_hosts):
    nm.scan(host,arguments='--exclude-ports 9999')
    info_hosts[host]={}
    info_hosts[host]['name']=nm[host]['hostnames'][0]['name']  
    for proto in nm[host].all_protocols():
        info_hosts[host]['protocol']=proto

        lport = nm[host][proto].keys()
        #lport.sort()
        
        aux=[]
        for port in lport:
            aux.append(str(port))
        info_hosts[host]['ports']=','.join(aux)
                
rede_info= None

def obter_info_hosts():
    global rede_info
    hosts_verificados=verifica_hosts()
    nm = nmap.PortScanner()
    info_hosts= dict()
    for host in hosts_verificados:
        try:
            adiciona_info_portas(nm,host,info_hosts)
        except:
            pass
        
    rede_info = info_hosts 

thread_rede = Thread(target = obter_info_hosts, args = ())
thread_rede.start()

def get_hosts():
    global interface_rede_atual
    if thread_rede.is_alive():
        return 'carregando'
    else:    
        textos = []
        t="|{:^20}|{:^25}|{:^16}|{:^21}|"
        rede_text='Interface de rede mais utilizada: ' + interface_rede_atual[0]
        textos.append(rede_text)
        textos.append(t.format('Host','Nome','Protocolo','Portas'))
        thread_rede.join()
        hosts = rede_info
        UNKNOWN = 'Desconhecido'
        def getInfo(info):
            if info in hosts[host]:
                if hosts[host][info] == '':

                    return UNKNOWN
                return hosts[host][info]
            return UNKNOWN

        for idx,host in enumerate(hosts):
            label = t.format(host,getInfo('name'),getInfo('protocol'),getInfo('ports'))   
            textos.append(label)

        return textos

while True:
    (socket_cliente,addr) = socket_servidor.accept()	
    # Aceita alguma conexão
    print("Conectado a:", str(addr))
    resposta = ''
    msg = socket_cliente.recv(4096)
    # Decodifica mensagem em ASCII
    msg = pickle.loads(msg)
    print('Tipo requisicao:',msg['name'])
    if msg['name'] == 'monitoramento': 
        resposta = get_monitoramento()
    if msg['name'] == 'processos':
        page=msg['payload']
        resposta = get_processos(page)
    if msg['name'] == 'diretorios':
        resposta = get_diretorios()
    if msg['name'] == 'trafego_rede':
        resposta = get_trafego_rede()
    if msg['name'] == 'hosts':
        resposta = get_hosts()
    pickled= pickle.dumps(resposta)
    socket_cliente.send(pickled)
    socket_cliente.close()