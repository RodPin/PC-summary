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
    



# resposta = request({'name':'processos','payload':2})
# resposta = request({'name':'diretorios'})
# resposta = request({'name':'trafego_rede'})
# resposta = request({'name':'hosts'})
# resposta = request({'name':'monitoramento'})


import platform
import psutil
import pygame, sys
from pygame.locals import *
import cpuinfo 
import os
from datetime import datetime
import sched 
import time
import nmap
import subprocess
from threading import Thread

scheduler = sched.scheduler(time.time, time.sleep)

processador='Processador: '
rede=''
array=0 
sistema = platform.system()
info = cpuinfo.get_cpu_info()


PATH = os.path.abspath('./')


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

BLACK=(0,0,0)
WHITE=(255,255,255)
RED=(255,40,0)
GREEN=(0, 130, 36)
YELLOW=(238, 238, 0)
GREY=(60,60,60)

ALTURA_BARRA = 200
LARGURA_BARRA = 70
ESPACO_BARRA = 10

ESPACO_BARRAS_E_LEGENDA=10
TAMANHO_LEGENDA=100
BORDA=15

clock = pygame.time.Clock()

#  cpus_count + 2 pois a barra de Disco e de memoria sao fixas (2 barras a mais)
LARGURA_TELA= LARGURA_BARRA * (2+cpus_count) + ESPACO_BARRA*(2+cpus_count-1) + BORDA*2 + TAMANHO_LEGENDA + ESPACO_BARRAS_E_LEGENDA
LARGURA_TELA2= 1200
LEGENDA_X=LARGURA_TELA -ESPACO_BARRAS_E_LEGENDA- BORDA - TAMANHO_LEGENDA + ESPACO_BARRAS_E_LEGENDA
ALTURA_TELA=630
DISPLAY=pygame.display.set_mode((LARGURA_TELA2,ALTURA_TELA),0,32)


def inGB(m):
    if m is not None:
        return str(round(m/(1024*1024*1024),2))

pygame.init()

def desenhar_barra(label,percentage,i,total=0):
    #Define a fonte e o tamanho
    myfont = pygame.font.SysFont("Arial", 15)
    # Define o tamanho da superficie em que vamos desenhar
    surface = pygame.surface.Surface((80,273))
    # Define onde a barra sera desenhada horizontalmente
    BARRA_X=BORDA +ESPACO_BARRA*i + LARGURA_BARRA*i
    
    # Define onde a barra sera desenhada verticalmente
    BARRA_Y=15
    
    
    # Seta as cores se a porcentagem for menor que 70% verde, entre 70% e 90% amarelo e acima de 90% vermelho
    COLOR=GREEN
    if percentage>= 0.9:
        COLOR=RED
    elif percentage>=0.7:
        COLOR=YELLOW

    #Desenha o retangulo branco da barra
    pygame.draw.rect(surface,WHITE,(0,BARRA_Y,LARGURA_BARRA,ALTURA_BARRA-1))
    
    #Desenha o retangulo colorido da barra por cima do branco
    if(percentage != 0 ):
        pygame.draw.rect(surface,COLOR,(0,BARRA_Y+ ALTURA_BARRA - percentage*ALTURA_BARRA,LARGURA_BARRA,BARRA_Y+ALTURA_BARRA-(BARRA_Y+ ALTURA_BARRA - percentage*ALTURA_BARRA)))
        

    #Prepara o texto em baixo da barra
    label = myfont.render(label, 1, WHITE)
    porcentagem = myfont.render(str(round(percentage*100)) + '%', 1, WHITE)
    
    if total != 0:
        myfont2 = pygame.font.SysFont("Arial", 11)

        total=float(total)
        detalhes=myfont2.render(str(int(int(total)*percentage))+'/'+str(int(total))+'GB', 1, WHITE)
        surface.blit(detalhes,(15 , ALTURA_BARRA + BARRA_Y+30))

    #Desenha na tela o texto
    surface.blit(porcentagem, (20 , ALTURA_BARRA + BARRA_Y))
    surface.blit(label, (20 , ALTURA_BARRA + BARRA_Y+15))

    #Desenha a superficie na tela
    DISPLAY.blit(surface, (BARRA_X, 0))

def desenhar_legenda():

    def desenhar_legenda_unica(cor,label,cont):
        #Seta a font e tamanho
        myfont = pygame.font.SysFont("Arial", 12)
        #Seta a surface
        surface = pygame.surface.Surface((TAMANHO_LEGENDA+10, 12))
        #Seta o texto
        text= myfont.render(label, 1, WHITE)
        #Desenha o quadrado da cor
        pygame.draw.rect(surface,cor,(0,0,10,10))
        #Escreve o texto
        surface.blit(text, (19 , 0))
        #Desenha a surface na tela
        DISPLAY.blit(surface, ( LEGENDA_X, 20+cont*20 ))

    desenhar_legenda_unica(GREEN,'Menor que 70%',0)
    desenhar_legenda_unica(YELLOW,"Entre 70 e 90%",1)
    desenhar_legenda_unica(RED,'Maior que 90%',2)

def desenhar_bolinhas(index,array):
    surface = pygame.surface.Surface((50, 30))
    circles=len(array)
    color=RED
    for i in range(0,circles):
        if i == index or index==4:
            color=WHITE
        else:
            color=GREY
        pygame.draw.circle(surface, color, (10+12*i,8),5) 
    DISPLAY.blit(surface, ( 80,ALTURA_BARRA+70))

def desenhar_info(array):
    #Seta a font e tamanho
    myfont = pygame.font.SysFont("Arial", 15)
    title = pygame.font.SysFont("Arial", 23)
    surface = pygame.surface.Surface((LARGURA_TELA, 300))

    title_element= title.render(array[0], 1, WHITE)
    surface.blit(title_element,(40,0))

    for i,info in enumerate(array):
        if i!=0:
            #Seta os textos
            text= myfont.render(info, 1, WHITE)
            surface.blit(text, (0 , 30+i*17))
    
    DISPLAY.blit(surface,(20,ALTURA_BARRA+100))

def desenhar_monitoramento():
    global cont,CPUS
    resposta = request({'name':'monitoramento'})
    print(resposta)


    desenhar_bolinhas(index,resposta['infos'])
    desenhar_barra('Memoria',resposta['pct_memoria']/100,0)
    desenhar_barra('Disco',resposta['pct_disco']/100,1,inGB(resposta['disco'].total))
    
    for i,cpu in enumerate(resposta['CPUS']):
        desenhar_barra('CPU '+str(i+1),cpu/100,2+i)
        

    desenhar_legenda()
    desenhar_info(resposta['infos'][index])

def desenha_arquivos():
    textos=[]
    resposta = request({'name':'diretorios'})
    myfont = pygame.font.SysFont("Courier", 20)
    surface = pygame.surface.Surface((LARGURA_TELA2, 900))

    def escrever(label,namePath='',idx=None):
        textos.append(myfont.render(label,1, WHITE))
    
    
    for linha in resposta['lista']:
        escrever(linha)
    escrever(" Total ........  : "+str(resposta['total'])+" Arquivos e Diretorios")
    escrever(" Total de bytes utilizados : "+str(resposta['bytes_total']/1000)+" Kbytes")
        
    for idx,texto in enumerate(textos):
        surface.blit(texto, (2 , 25*idx))

    DISPLAY.blit(surface,(20,20))
    end_time=time.process_time()
    
process_count=0
page=0
page_size=20
pages=[]

def titulo():
    titulo = '{:^7}'.format("PID")
    titulo = titulo + '{:^11}'.format("# Threads")
    titulo = titulo + '{:^26}'.format("Criação")
    titulo = titulo + '{:^9}'.format("T. Usu.")
    titulo = titulo + '{:^9}'.format("T. Sis.")
    titulo = titulo + '{:^12}'.format("Memoria(%)")
    titulo = titulo + '{:^12}'.format("RSS")
    titulo = titulo + '{:^12}'.format("VMS")
    titulo = titulo + " Executável"
    return titulo

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

pagina=2
def desenha_processos():
    global pagina
    initial_time=time.process_time()
    myfont = pygame.font.SysFont("Courier", 15)
    surface = pygame.surface.Surface((LARGURA_TELA2, 2000))

    def escrever(label,idx):
        txt=myfont.render(label,1, WHITE)
        surface.blit(txt, (2 ,100 +   20*idx))

    resposta = request({'name':'processos','payload':pagina})
    escrever('Quantidade de processos: '+str(resposta['qtd']),-3)
    escrever('Pagina '+str(pagina)+'/'+str(resposta['max']),-2)
    for idx,line in enumerate(resposta['pagina']):
        escrever(line,idx)

       
    DISPLAY.blit(surface,(20,20))
    end_time=time.process_time()


#############################################    
interface_rede_atual = ['',0]
def desenha_hosts():
    global interface_rede_atual    
    
    myfont = pygame.font.SysFont("Courier", 20)
    surface = pygame.surface.Surface((LARGURA_TELA2, 900))
    surface2 = pygame.surface.Surface((LARGURA_TELA2, 200))
    textos=[]

    if thread_rede.is_alive():
        texto=myfont.render('Consultando informacoes de rede...',1,WHITE)
        surface.blit(texto, (0 , 0))       
        DISPLAY.blit(surface,(400,300))
    else:    
        t="|{:^20}|{:^25}|{:^16}|{:^21}|"
        rede_text='Interface de rede mais utilizada: ' + interface_rede_atual[0]
        textos.append(myfont.render(rede_text,1,WHITE))
        textos.append(myfont.render(t.format('Host','Nome','Protocolo','Portas'),1, WHITE))
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
            textos.append(myfont.render(label,1, WHITE))

        for idx,texto in enumerate(textos):
            surface.blit(texto, (2 ,25*idx))       
         
        DISPLAY.blit(surface,(20,300))


    redes_infos = psutil.net_io_counters(pernic=True)
    t2="|{:^20}|{:^20}|{:^20}|{:^20}|{:^20}|"
    textos_rede_info=[]        
    textos_rede_info.append(myfont.render(t2.format('Interface','Bytes enviados','Bytes Recebidos','Pacotes enviados','Pacotes recebidos'),1, WHITE))
    for info_rede in redes_infos:
        ri_dic=redes_infos[info_rede]
        label = t2.format(info_rede,ri_dic.bytes_sent,ri_dic.bytes_recv,ri_dic.packets_sent,ri_dic.packets_recv)
        textos_rede_info.append(myfont.render(label,1, WHITE))  

        if interface_rede_atual[1] < ri_dic.bytes_sent:
            interface_rede_atual[0]=info_rede
            interface_rede_atual[1]= ri_dic.bytes_sent
    
    for idx,texto in enumerate(textos_rede_info): 
        surface2.blit(texto, (2 ,25*idx))             

    DISPLAY.blit(surface2,(20,20))


DISPLAY.fill(BLACK)
index=0
index_copy=None
clock.tick(60)
CPUS=psutil.cpu_percent(interval=0.1, percpu=True)
cont=0

mouseIn=False
surfaceVoltar = pygame.surface.Surface((102,29))
idxMouseOnTop=''
dirs=[]
aba=3
while True:
    DISPLAY.fill(BLACK)

    for event in pygame.event.get():
        if event.type==QUIT:
            pygame.quit()
            sys.exit() 
        #============================================================== Mudanca de aba
        if event.type == pygame.KEYDOWN :
            if event.key == pygame.K_1:
                DISPLAY=pygame.display.set_mode((LARGURA_TELA,ALTURA_TELA),0,32)
                aba=1
            if event.key == pygame.K_2:
                DISPLAY=pygame.display.set_mode((LARGURA_TELA2,ALTURA_TELA),0,32)
                aba=2
            if event.key == pygame.K_3:
                DISPLAY=pygame.display.set_mode((LARGURA_TELA2+100,ALTURA_TELA),0,32)
                aba=3
            if event.key == pygame.K_4:
                DISPLAY=pygame.display.set_mode((LARGURA_TELA2+100,ALTURA_TELA),0,32)
                aba=4
        #============================================================== Primeira ABA
        if aba ==1:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if index > 0  and index != 4:
                        index=index-1
                if event.key == pygame.K_RIGHT:
                    if index < 3 and index != 4:
                        index=index+1
                if event.key == pygame.K_SPACE:
                    if index_copy == None:
                        index_copy=index
                        index=4
                    else:
                        index=index_copy
                        index_copy=None
        
        #============================================================== Segunda Aba
        if aba==2:
            if event.type == MOUSEMOTION:
                mouseX,mouseY = event.pos
                if mouseX>32 and mouseX <134 and mouseY>38 and mouseY<67:
                    mouseIn=True
                else:
                    mouseIn=False
                    
            if event.type == pygame.MOUSEBUTTONUP:  # or MOUSEBUTTONDOWN depending on what you want.
                mouseX,mouseY=event.pos
                if mouseX>32 and mouseX <134 and mouseY>38 and mouseY<67:
                    voltarPath()

            if event.type == MOUSEMOTION or event.type == pygame.MOUSEBUTTONUP and mouseX > 30 and mouseX <  1120:
                mouseX,mouseY = event.pos
        
                firstY=147
                if mouseY>firstY:
                    idxMouseOnTop=int((mouseY-firstY)/25)
                    if event.type == pygame.MOUSEBUTTONUP:
                        clickEntrar(PATH+'/'+dirs[idxMouseOnTop])
                else:
                    idxMouseOnTop=False
            #==============================================================
        if aba ==3:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT and page < len(pages)-1:
                    page=page+1
                if event.key == pygame.K_LEFT and page > 0:
                    page=page-1
        

    if aba == 1:
        desenhar_monitoramento()
    if aba == 2:
        scheduler.enter(0, 1, desenha_arquivos, ())
    if aba == 3:
        desenha_processos()
    # # if aba == 4:
    # #     desenha_hosts()
    scheduler.run()
    pygame.display.update()
    time.sleep(10)
    break

