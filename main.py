__author__ = 'blacKnight'
import pygame
import sys
import os
import random
import vars
import mainMenu
from pygame.locals import *


#This will initiate the program
#initialize modules, open splash screen, open main menu
def main():
    pygame.init()

    splashScreenSurf = pygame.display.set_mode((400, 400))
    splashScreenFPSClock = pygame.time.Clock()

    SplashScreen(splashScreenSurf, splashScreenFPSClock)

    vars.DISP = pygame.display.set_mode((vars.WINW, vars.WINH))
    vars.FPSCLOCK = pygame.time.Clock()

    mainMenu.main()


#quick little screen that should last for ~2 seconds
def SplashScreen(Surface, FPSClock):
    looper = True
    splashText = vars.Text('blacKnight gaMing', None, 32, vars.WHITE, vars.BLACK)
    splashText.rect.centerx = 200
    splashText.rect.centery = 200
    ticker = 0

    while looper:
        Surface.fill(vars.BLACK)
        splashText.Draw(Surface)
        ticker += 1
        if ticker > 20:
            looper = False

        pygame.display.update()
        FPSClock.tick(vars.FPS)


def Terminate():
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()