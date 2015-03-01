__author__ = 'black_000'
import pygame
import sys
import os
import copy
import random
import vars
import engine
from pygame.locals import *

def main():
    drawList = []
    #Realtor Domain title
    titleText = vars.Text('Realtor Domain', None, 120)
    titleText.rect.centerx = vars.WINW*.4
    titleText.rect.top = 100
    drawList.append(titleText)
    #Menu Items
    menuText = []
    menuText.append(vars.Text('New Game', None, 80))
    menuText[0].rect.left = titleText.rect.left + 100
    menuText[0].rect.top = titleText.rect.top + 150
    menuText.append(vars.Text('Developer', None, 80))
    menuText[1].rect.topleft = (menuText[0].rect.left, menuText[0].rect.top + 100)
    drawList.append(menuText[0])
    drawList.append(menuText[1])

    loop = True
    while loop:
        for event in pygame.event.get():
            if event.type == QUIT:
                Terminate()
            if event.type == MOUSEBUTTONDOWN:
                if menuText[1].rect.collidepoint(event.pos):
                    engine.main(True)
        vars.DISP.fill(vars.BLACK)
        for i in range(len(drawList)):
            drawList[i].Draw()
        pygame.display.update()
        vars.FPSCLOCK.tick(vars.FPS)

def Terminate():
    pygame.quit()
    sys.exit()