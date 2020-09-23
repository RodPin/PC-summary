import platform
import psutil
import pygame, sys
from pygame.locals import *
import time
from cpuinfo import get_cpu_info

processador='Processador: '
rede=''
array=0 
sistema = platform.system()
if sistema == 'Linux':
    rede='wlp3s0'
    processador += get_cpu_info()['brand_raw']
elif sistema == 'Windows':
    rede='Wi-Fi'
    array=1
    processador += platform.processor()
else:
    processador += get_cpu_info()['brand_raw']
    rede='en0'

ip= 'IP: '+ psutil.net_if_addrs()[rede][array].address



BLACK=(0,0,0)
WHITE=(255,255,255)
RED=(255,40,0)
GREEN=(0, 130, 36)
YELLOW=(238, 238, 0)

ALTURA_BARRA = 200
LARGURA_BARRA = 70
ESPACO_BARRA = 10

LARGURA_TELA=530
ALTURA_TELA=330
DISPLAY=pygame.display.set_mode((LARGURA_TELA,ALTURA_TELA),0,32)

clock = pygame.time.Clock()

def desenhar_barra(label,percentage,i):
    #Define a fonte e o tamanho
    myfont = pygame.font.SysFont("Arial", 15)
    # Define o tamanho da superficie em que vamos desenhar
    surface = pygame.surface.Surface((80,260))
    surface.fill(BLACK)
    # Define onde a barra sera desenhada horizontalmente
    BARRA_X=ESPACO_BARRA + ESPACO_BARRA*i + LARGURA_BARRA*i
    
    # Define onde a barra sera desenhada verticalmente
    BARRA_Y=15
    
    # Seta as cores se a porcentagem for menor que 70% verde, entre 70% e 90% amarelo e acima de 90% vermelho
    COLOR=GREEN
    if percentage>= 0.9:
        COLOR=RED
    elif percentage>=0.7:
        COLOR=YELLOW

    #Desenha o retangulo branco da barra
    pygame.draw.rect(surface,WHITE,(15,BARRA_Y,LARGURA_BARRA,ALTURA_BARRA-1))
    
    #Desenha o retangulo colorido da barra por cima do branco
    if(percentage != 0 ):
        pygame.draw.rect(surface,COLOR,(15,BARRA_Y+ ALTURA_BARRA - percentage*ALTURA_BARRA,LARGURA_BARRA,BARRA_Y+ALTURA_BARRA-(BARRA_Y+ ALTURA_BARRA - percentage*ALTURA_BARRA)))
        

    #Prepara o texto em baixo da barra
    label = myfont.render(label, 1, WHITE)
    porcentagem = myfont.render( "{:.2f}".format(percentage*100) + '%', 1, WHITE)

    #Desenha na tela o texto
    surface.blit(porcentagem, (20 , ALTURA_BARRA + BARRA_Y))
    surface.blit(label, (20 , ALTURA_BARRA + BARRA_Y+15))

    #Desenha a superficie na tela
    DISPLAY.blit(surface, (BARRA_X, 0))

def desenhar_info():
    #Seta a font e tamanho
    myfont = pygame.font.SysFont("Arial", 15)
    surface = pygame.surface.Surface((LARGURA_TELA, 50))

    #Seta os textos
    ip_text =  myfont.render(ip, 1, WHITE)
    cpu_text =  myfont.render(processador, 1, WHITE)
    #Desenha os textos na surface
    surface.blit(ip_text, (0 , 0))
    surface.blit(cpu_text, (0 , 30))
    #Desenha a surface na tela
    DISPLAY.blit(surface,(20,ALTURA_BARRA+70))

def desenhar_legenda():

    def desenhar_legenda_unica(cor,label,cont):
        #Seta a font e tamanho
        myfont = pygame.font.SysFont("Arial", 12)
        #Seta a surface
        surface = pygame.surface.Surface((100, 12))
        #Seta o texto
        text= myfont.render(label, 1, WHITE)
        #Desenha o quadrado da cor
        pygame.draw.rect(surface,cor,(0,0,10,10))
        #Escreve o texto
        surface.blit(text, (19 , 0))
        #Desenha a surface na tela
        DISPLAY.blit(surface, (300 , 20+cont*20 ))

    desenhar_legenda_unica(GREEN,'Menor que 70%',0)
    desenhar_legenda_unica(YELLOW,"Entre 70 e 90%",1)
    desenhar_legenda_unica(RED,'Maior que 90%',2)



def main():
    pygame.init()

    DISPLAY.fill(BLACK)


    while True:
        for event in pygame.event.get():
            if event.type==QUIT:
                pygame.quit()
                sys.exit() 

        pct_memoria = psutil.virtual_memory().percent
        pct_cpu = psutil.cpu_percent()
        pct_disco = psutil.disk_usage('.').percent

        desenhar_barra('Memoria',pct_memoria/100,0)
        desenhar_barra('CPU',pct_cpu/100,1)
        desenhar_barra('Disco',pct_disco/100,2)

        desenhar_info()
        
        desenhar_legenda()

        pygame.display.update()
        clock.tick(60)
        time.sleep(1)

main()