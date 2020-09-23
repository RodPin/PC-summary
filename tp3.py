import platform
import psutil
import pygame, sys
from pygame.locals import *
import cpuinfo 

processador='Processador: '
rede=''
array=0 
sistema = platform.system()

info = cpuinfo.get_cpu_info()

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
LEGENDA_X=LARGURA_TELA -ESPACO_BARRAS_E_LEGENDA- BORDA - TAMANHO_LEGENDA + ESPACO_BARRAS_E_LEGENDA
ALTURA_TELA=630
DISPLAY=pygame.display.set_mode((LARGURA_TELA,ALTURA_TELA),0,32)


def inGB(m):
    return str(round(m/(1024*1024*1024),2))

pygame.init()

def desenhar_barra(label,percentage,i):
    #Define a fonte e o tamanho
    myfont = pygame.font.SysFont("Arial", 15)
    # Define o tamanho da superficie em que vamos desenhar
    surface = pygame.surface.Surface((80,260))
    surface.fill(BLACK)
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
    surface.fill(BLACK)

    title_element= title.render(array[0], 1, WHITE)
    surface.blit(title_element,(40,0))

    for i,info in enumerate(array):
        if i!=0:
            #Seta os textos
            text= myfont.render(info, 1, WHITE)
            surface.blit(text, (0 , 30+i*17))
    
    DISPLAY.blit(surface,(20,ALTURA_BARRA+100))


DISPLAY.fill(BLACK)
index=0
index_copy=None
clock.tick(60)

while True:
    for event in pygame.event.get():
        if event.type==QUIT:
            pygame.quit()
            sys.exit() 
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

    frequencia='Frequencia: '+ str(round(psutil.cpu_freq().current,2)) + 'MHz'
    
    #Memoria
    mem = psutil.virtual_memory()
    memoria_total="Memoria Total:"+ inGB(mem.total)+ " GB"
    memoria_disponivel="Memoria Disponivel:"+ inGB(mem.available)+ " GB"
    memoria_livre="Memoria Livre:"+ inGB(mem.free)+ " GB"
    memoria_usada="Memoria Usada:"+ inGB(mem.used)+ " GB"
    
    net= psutil.net_if_addrs()[rede][array]
    ip= 'IP: '+ net.address
    netmask='NetMask: '+net.netmask
    family='Family: ' + str(net.family)
    ptp='Ptp: '+str(net.ptp)
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
        net_os=['BroadCast: '+net.broadcast]

    disco=psutil.disk_usage('.')
    disco_total='Disco Total: '+ inGB(disco.total) +' GB'
    disco_usado='Disco Usado: '+ inGB(disco.used)+' GB'
    disco_livre='Disco Livre: '+ inGB(disco.free)+' GB'
    


    processador_info=['Processador:',nome,arquitetura,frequencia_total,frequencia,bits,cpuscount,cpuscountfisical]
    memoria_info=['Memoria: ', memoria_total,memoria_disponivel,memoria_usada,memoria_livre]+memoria_os
    disco_info=['Disco:',disco_total,disco_usado,disco_livre]
    net_info=['Rede:',ip,netmask,family,ptp]+net_os
    resumo_info=['Resumo: ',nome,cpuscount,memoria_total,memoria_disponivel,memoria_usada,memoria_livre,disco_total,disco_usado,disco_livre,ip,netmask]

    infos=[processador_info,memoria_info,disco_info,net_info,resumo_info]


    pct_memoria = psutil.virtual_memory().percent
    pct_cpu = psutil.cpu_percent()
    pct_disco = psutil.disk_usage('.').percent

    desenhar_bolinhas(index,infos)

    desenhar_barra('Memoria',pct_memoria/100,0)
    desenhar_barra('Disco',pct_disco/100,1)
    for i,cpu in enumerate(psutil.cpu_percent(interval=1, percpu=True)):
        desenhar_barra('CPU '+str(i+1),cpu/100,2+i)
        

    desenhar_legenda()

    desenhar_info(infos[index])

    pygame.display.update()

