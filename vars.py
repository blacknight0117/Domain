__author__ = 'black_000'
import pygame
import os
import copy
import random
from pygame.locals import *

WINW = 1150
WINH = 900

WINXCTR = WINW/2
WINYCTR = WINH/2

MAPX = 0
MAPY = 0

DETAILSX = 900
DETAILSY = 150
DETAILSW = 250

INFOX = 900
INFOY = 0

pygame.init()
DISP = pygame.display.set_mode((WINW, WINH))
FPSCLOCK = None
FPS = 45

WHITE   = Color('white')
BLACK   = Color('black')
LTGREY  = (200, 200, 200, 255)
GREY    = (150, 150, 150, 255)
DKGREY  = (100, 100, 100, 255)
VDKGREY = (50, 50, 50, 255)
RED     = (100, 0, 0, 255)
BTRED   = (200, 0, 0, 255)
ZRED    = (255, 0, 0, 255)
BLUE    = (0, 0, 100, 255)
GREEN   = (0, 100, 0, 255)
YELLOW  = (100, 100, 0, 255)
BTYELL  = (255, 255, 0, 255)

#Finding random building info
BUILDINGTYPES = ['Residential', 'Residential', 'Residential', 'Residential', 'Retail',
                 'Retail', 'Retail', 'Office', 'Office', 'Parking', 'Parking']
BUILDINGFLOORS = [1, 1, 1, 2, 3, 3]
BUILDINGNAMES = ['Alpha', 'Bravo', 'Charlie', 'Delta', 'Echo', 'Foxtrot', 'Golf', 'Hotel', 'India']
BUILDINGVALUES = [1000, 1000, 1000, 2000, 3000, 4000]

COSTADDFLOOR = 4000
COSTTRANSFORM = 1000
COSTDESTROY = [2000, 4000, 5500, 7000]
COSTBUILD = 6000

class Font():
    def __init__(self, aFile, aSize):
        self.fontFile = aFile
        self.fontSize = aSize
        self.font = None
        self.Setup()

    def Setup(self):
        self.font = pygame.font.Font(self.fontFile, self.fontSize)


class Text():
    def __init__(self, someText, aFontFile, aFontSize, textColor=WHITE, bgColor=None):
        self.text = someText
        self.selected = False
        self.selectedSurf = None
        self.loc = [0, 0]
        self.font = Font(aFontFile, aFontSize)
        self.fontSize = aFontSize
        self.surf = None
        self.rect = None
        self.color = textColor
        self.bgColor = bgColor
        self.Setup()

    #Initialize fontRect
    def Setup(self):
        if self.bgColor is not None:
            self.surf = self.font.font.render(self.text, 1,
                                              self.color,
                                              self.bgColor).convert()
            self.selectedSurf = self.font.font.render(self.text, 1,
                                                      InvertColor(self.color),
                                                      InvertColor(self.bgColor)).convert()
        else:
            self.surf = self.font.font.render(self.text, 0,
                                              self.color).convert()
            self.selectedSurf = self.font.font.render(self.text, 0,
                                                      InvertColor(self.color)).convert()

        self.surf.set_alpha(255)
        self.rect = self.surf.get_rect()

    #Draws border if selected, else just output to DisplaySurf
    def Draw(self, aSurf=DISP):
        if self.selected:
            aSurf.blit(self.selectedSurf, self.rect)
        else:
            aSurf.blit(self.surf, self.rect)

    def ChangeSize(self, increment, newFile):
        tempRect = self.rect
        self.font = Font(newFile, self.fontSize + increment)
        if self.bgColor is not None:
            self.surf = self.font.font.render(self.text, 1,
                                              self.color,
                                              self.bgColor).convert()
            self.selectedSurf = self.font.font.render(self.text, 1,
                                                      InvertColor(self.color),
                                                      InvertColor(self.bgColor)).convert()
        else:
            self.surf = self.font.font.render(self.text, 0,
                                              self.color).convert()
            self.selectedSurf = self.font.font.render(self.text, 0,
                                                      InvertColor(self.color)).convert()
        self.surf.set_alpha(255)
        self.rect.topleft = tempRect.topleft

    def ChangeAlpha(self, aVal):
        self.surf.set_alpha(aVal)


class Button():
    def __init__(self, string, rect, border=4, color=WHITE, textColor=BLACK):
        self.string = string
        self.text = [Text(string, None, rect.height-4, textColor),
                     Text(string, None, rect.height-4, color)]
        self.rect = rect
        self.text[0].rect.center = self.rect.center
        self.text[1].rect.center = self.rect.center
        self.border = border
        self.color = color
        self.textColor = textColor
        self.pushed = False
        self.counter = 0
        self.void = False

    def LocCollide(self, aPos):
        if not self.void:
            self.pushed = self.rect.collidepoint(aPos)
            self.counter = 6
            return self.pushed
        return False

    def Draw(self):
        if self.pushed:
            pygame.draw.rect(DISP, self.color, self.rect.inflate(2, 2))
            pygame.draw.rect(DISP, self.textColor, self.rect)
            self.text[1].Draw()
            self.counter -= 1
            if not self.counter:
                self.pushed = False
        else:
            pygame.draw.rect(DISP, self.textColor, self.rect.inflate(2, 2))
            pygame.draw.rect(DISP, self.color, self.rect)
            self.text[0].Draw()
            if self.void:
                tempSurf = pygame.Surface((self.rect.width, self.rect.height))
                tempSurf.set_alpha(200)
                tempSurf.fill(DarkenColor(self.color))
                DISP.blit(tempSurf, self.rect.topleft)


def DarkenColor(aColor):
    temp = copy.deepcopy(aColor)
    return temp[0]/2, temp[1]/2, temp[2]/2, temp[3]


def TransparentColor(aColor, aVal):
    temp = copy.deepcopy(aColor)
    return temp[0], temp[1], temp[2], temp[3]*aVal


def InvertColor(aColor):
    temp = copy.deepcopy(aColor)
    return 255-temp[0], 255-temp[1], 255-temp[2], temp[3]