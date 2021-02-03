import socket,time,pickle
import platform
import psutil
import pygame, sys
from pygame.locals import *
import cpuinfo 
import os
import sched 
import time


host = socket.gethostname()


def request(message):
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        s.connect((host,9999))
        message = pickle.dumps(message)
        s.send(message)
        data = s.recv(4096)
        s.close()
        return pickle.loads(data)
    except Exception as erro:
        print('Servidor desligado, tentando reconexao')
        time.sleep(5)
        return request(message)

scheduler = sched.scheduler(time.time, time.sleep)

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
LARGURA_TELA= 1300
LEGENDA_X=LARGURA_TELA -ESPACO_BARRAS_E_LEGENDA- BORDA - TAMANHO_LEGENDA + ESPACO_BARRAS_E_LEGENDA
ALTURA_TELA=630
DISPLAY=pygame.display.set_mode((LARGURA_TELA,ALTURA_TELA),0,32)


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

    surface.blit(myfont.render('Utilize ↑ ↓ para navegar',1, WHITE),(280,0))

    for i,info in enumerate(array):
        if i!=0:
            #Seta os textos
            text= myfont.render(info, 1, WHITE)
            surface.blit(text, (0 , 30+i*17))
    
    DISPLAY.blit(surface,(20,ALTURA_BARRA+100))

def desenhar_monitoramento():
    resposta = request({'name':'monitoramento'})


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
    surface = pygame.surface.Surface((LARGURA_TELA, 900))

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
    

pagina=0
max_pagina=0

def desenha_processos():
    global pagina , max_pagina
    initial_time=time.process_time()
    myfont = pygame.font.SysFont("Courier", 16)
    myfont2 = pygame.font.SysFont("Arial", 16)
    surface = pygame.surface.Surface((LARGURA_TELA, 2000))

    def escrever(label,idx):
        txt=myfont.render(label,1, WHITE)
        surface.blit(txt, (2 ,100 +   20*idx))

    def escrever2(label,idx):
        surface.blit(myfont2.render(label,1, WHITE), (2 ,100 +   20*idx))
    resposta = request({'name':'processos','payload':pagina})

    max_pagina = resposta['max']
    
    escrever2('Utilize ↑ ↓ para navegar',-4)
    escrever2('Quantidade de processos: '+str(resposta['qtd']),-3)
    escrever2('Pagina '+str(pagina+1)+'/'+str(resposta['max']+1),-2)

    for idx,line in enumerate(resposta['pagina']):
        escrever(line,idx)

       
    DISPLAY.blit(surface,(20,20))
    end_time=time.process_time()


def desenha_hosts():
    myfont = pygame.font.SysFont("Courier", 20)
    surface = pygame.surface.Surface((LARGURA_TELA, 900))
    surface2 = pygame.surface.Surface((LARGURA_TELA, 200))
    
    def escrever(texto):
        return myfont.render(texto,1, WHITE)

    resposta = request({'name':'hosts'})

    if resposta=='carregando':
        texto=myfont.render('Consultando informacoes de rede...',1,WHITE)
        surface.blit(texto, (0 , 0))       
        DISPLAY.blit(surface,(400,300))
    else:    
        for idx,texto in enumerate(resposta):
            surface.blit(escrever(texto), (2 ,25*idx))       
         
    DISPLAY.blit(surface,(20,300))


    resposta2 = request({'name':'trafego_rede'})

    for idx,texto in enumerate(resposta2): 
        surface2.blit(escrever(texto), (2 ,25*idx))             

    DISPLAY.blit(surface2,(20,20))


def desenha_navegacao():
    myfont = pygame.font.SysFont("Arial", 15)
    surface = pygame.surface.Surface((LARGURA_TELA, 300))
    surface.blit(myfont.render('Utilize ← ou → para navegar',1, WHITE),(280,0))
    DISPLAY.blit(surface,(220,ALTURA_TELA-40))

DISPLAY.fill(BLACK)
index=0
index_copy=None
clock.tick(60)
CPUS=psutil.cpu_percent(interval=0.1, percpu=True)

aba=1

while True:
    DISPLAY.fill(BLACK)

    for event in pygame.event.get():
        if event.type==QUIT:
            pygame.quit()
            sys.exit() 
        #============================================================== Mudanca de aba
        if event.type == pygame.KEYDOWN :
            if event.key == pygame.K_LEFT:
                if aba > 1:
                    aba=aba-1
            if event.key == pygame.K_RIGHT:
                if aba < 4:
                    aba=aba+1
        #============================================================== Primeira ABA
        if aba == 1:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    if index > 0  and index != 4:
                        index=index-1
                if event.key == pygame.K_DOWN:
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
            print('aba2')
            #==============================================================
        if aba ==3:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and pagina < max_pagina:
                    pagina=pagina+1
                if event.key == pygame.K_DOWN and pagina > 0:
                    pagina=pagina-1
        

    if aba == 1:
        desenhar_monitoramento()
    if aba == 2:
        scheduler.enter(0, 1, desenha_arquivos, ())
        scheduler.run()
    if aba == 3:
        desenha_processos()
    if aba == 4:
        desenha_hosts()

    desenha_navegacao()
    
    pygame.display.update()

