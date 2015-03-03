__author__ = 'black_000'
import pygame
import copy
import sys
import os
import random
import vars
from pygame.locals import *


def main(devCheck=False):
    global player, theMap
    theMap = Map()
    #initialize vars and inputs for dev environmment
    if devCheck:
        devMap = Map()
        Parser('MapData', devMap)
        theMap = devMap

    player = Owner()
    player.isPlayer = True
    player.name = 'blacKnight'
    player.Starting()
    currentSelected = Selected()

    #This is main engine game loop
    loop = True
    while loop:
        for event in pygame.event.get():
            if event.type == QUIT:
                Terminate()
            elif event.type == MOUSEBUTTONDOWN:
                temp = theMap.Click(event.pos)
                if temp is not None:
                    if currentSelected.selected is not None:
                        currentSelected.selected.highlight = False
                    currentSelected.Init(temp)
                    currentSelected.selected.highlight = True
                else:
                    currentSelected.Input(event.type, event.pos)

        currentSelected.Update()
        player.Update()
        
        vars.DISP.fill(vars.VDKGREY)
        player.DrawPlayer()
        theMap.Draw()
        currentSelected.Draw()
        pygame.display.update()
        vars.FPSCLOCK.tick(vars.FPS)


def Parser(fileName, aMap):
    fileData = open(fileName, 'r')
    for line in fileData:
        if len(line) != 1:
            if line[0] == '!':
                aMap.AddBlock(line[1:])
            elif aMap.size == 0:
                aMap.size = int(line[0])
            elif aMap.blockSize == 0:
                aMap.blockSize = int(line[0])
            elif line[0] == '#':
                pass
            else:
                print('Error D01: Map Data File not properly configured')


class Selected():
    def __init__(self):
        self.selected = None
        self.title = None
        self.address = None
        self.type = None
        self.floors = None          # holds additional floor
        self.rooms = None
        self.owner = None
        self.tenants = None
        self.shape = None
        self.price = None
        self.buttons = []
        self.empty = False

    def Init(self, newSelected):
        self.__init__()
        self.selected = newSelected
        self.selected.dirty = True
        if self.selected.floors == 0:
            self.empty = True

        #Used for Button placement
        temp = pygame.Rect(vars.DETAILSX+10, vars.DETAILSY+48+(32*5)+10, 50, 30)
        self.buttons.append(vars.Button('Buy', temp))
        self.buttons.append(vars.Button('Sell',
                                        pygame.Rect(temp.left + 180,
                                                    temp.top, 50, 30)))
        self.buttons.append(vars.Button('Add a Floor',
                                        pygame.Rect(temp.left,
                                                    temp.bottom + 10, 110, 30)))
        self.buttons.append(vars.Button('Transform',
                                        pygame.Rect(temp.left + 120,
                                                    temp.bottom + 10, 100, 30)))
        self.buttons.append(vars.Button('Destroy',
                                        pygame.Rect(temp.left,
                                                    temp.bottom + 80, 80, 30)))
        self.buttons.append(vars.Button('Build',
                                        pygame.Rect(temp.left + 170,
                                                    temp.bottom + 80, 60, 30)))

        self.Update()

    def Update(self):
        if self.selected is not None and self.selected.dirty:
            #Update all the selected info text
            self.title = vars.Text(self.selected.name, None, 48,
                                   vars.WHITE, vars.VDKGREY)
            self.address = vars.Text('Feature to be Coded.', None, 32,
                                     vars.WHITE, vars.VDKGREY)
            self.owner = vars.Text('Owner: ' + self.selected.owner, None, 32,
                                   vars.WHITE, vars.VDKGREY)
            if self.selected.owner == player.name:
                adjustVal = .75
            else:
                adjustVal = 1.25
            self.price = vars.Text('Price: ' + str(self.selected.value*adjustVal), None, 32,
                                   vars.WHITE, vars.VDKGREY)

            #Reset all the rect positioning
            self.title.rect.topleft = [vars.DETAILSX + 10, vars.DETAILSY + 10]
            self.address.rect.topleft = self.title.rect.bottomleft
            self.owner.rect.topleft = self.address.rect.bottomleft
            self.price.rect.topleft = self.owner.rect.bottomleft

            #If this isn't an empty lot we need the building information
            if not self.empty:
                self.type = vars.Text(self.selected.type + ' Building', None, 32,
                                      vars.WHITE, vars.VDKGREY)
                self.shape = vars.Text(self.selected.shape, None, 32,
                                       vars.WHITE, vars.VDKGREY)
                temp = str(self.selected.floors) + ' + ' + \
                    str(int(self.selected.additionalFloor))
                self.floors = vars.Text(temp + ' floors', None, 32,
                                        vars.WHITE, vars.VDKGREY)

                self.type.rect.topleft = self.price.rect.bottomleft
                self.shape.rect.topleft = self.type.rect.bottomleft
                self.floors.rect.topleft = self.shape.rect.bottomleft
            #Reset the dirty flag
            self.selected.dirty = False

            #Readjust the button voids
            for i in range(len(self.buttons)):
                self.buttons[i].void = False
            if self.selected.owner == player.name:
                self.buttons[0].void = True
                self.buttons[1].void = False
                if self.selected.additionalFloor:
                    self.buttons[2].void = True
                if (self.selected.type != 'Retail' and
                        self.selected.type != 'Residential'):
                    self.buttons[3].void = True
                if self.empty:
                    self.buttons[4].void = True
                    self.buttons[5].void = False
                else:
                    self.buttons[4].void = False
                    self.buttons[5].void = True
            else:
                self.buttons[0].void = False
                for i in range(len(self.buttons)):
                    if i != 0:
                        self.buttons[i].void = True

    def Input(self, aType, aPos):
        if aType == MOUSEBUTTONDOWN:
            for i in range(len(self.buttons)):
                if self.buttons[i].LocCollide(aPos):
                    if i == 0:
                        self.selected.owner = player.name
                        self.selected.dirty = True
                        player.cash -= self.selected.value * 1.25
                        player.dirty = True
                    elif i == 1:
                        self.selected.owner = 'The Bank'
                        self.selected.dirty = True
                        player.cash += self.selected.value * .75
                        player.dirty = True
                    elif i == 2 and not self.selected.additionalFloor:
                        self.selected.additionalFloor = True
                        self.selected.dirty = True
                        self.selected.Update()
                        player.cash -= vars.COSTADDFLOOR
                        player.dirty = True
                    elif i == 3:
                        if self.selected.type == 'Retail':
                            self.selected.ChangeType('Residential')
                            self.selected.dirty = True
                            self.selected.Update()
                            player.cash -= vars.COSTTRANSFORM
                            player.dirty = True
                        elif self.selected.type == 'Residential':
                            self.selected.ChangeType('Retail')
                            self.selected.dirty = True
                            self.selected.Update()
                            player.cash -= vars.COSTTRANSFORM
                            player.dirty = True
                        else:
                            print('ERROR E01: Building is not of the right type to Transform')
                    elif i == 4:
                        player.cash -= vars.COSTDESTROY[self.selected.floors+int(self.selected.additionalFloor)-1]
                        player.dirty = True
                        self.Init(theMap.blocks[self.selected.block].DestroyBuilding(self.selected.index))
                    elif i == 5:
                        player.cash -= vars.COSTBUILD
                        player.dirty = True
                        self.Init(theMap.blocks[self.selected.block].AddBuilding(self.selected.index))

    def Draw(self):
        pygame.draw.rect(vars.DISP, vars.WHITE,
                         (vars.DETAILSX, vars.DETAILSY, vars.DETAILSW, 4))
        if self.selected is not None:
            self.title.Draw()
            self.address.Draw()
            self.owner.Draw()
            self.price.Draw()
            if not self.empty:
                self.type.Draw()
                self.shape.Draw()
                self.floors.Draw()
            for i in range(len(self.buttons)):
                self.buttons[i].Draw()


class Map():
    def __init__(self):
        self.size = 0
        self.blockSize = 0
        self.blocks = []
        self.showFloors = True
        self.showSpecial = True
        self.mapButtons = []
        self.mapButtons.append(vars.Button('Floors',
                                           pygame.Rect(910, vars.WINH-35, 60, 25)))
        self.mapButtons.append(vars.Button('Specials',
                                           pygame.Rect(980, vars.WINH-35, 65, 25)))

    def AddBlock(self, aLine):
        if len(aLine) != (self.blockSize*self.blockSize)+1:
            print('Error D02: Map Data File not properly configured')
            print(str(len(aLine)))
        newBlock = Block(len(self.blocks))
        refString = 'abcdefghi'
        for i in range(len(refString)):
            temp = []
            for j in range(len(aLine)):
                if aLine[j] == refString[i]:
                    temp.append(j)
            if len(temp) != 0:
                newBuilding = Building(len(self.blocks), i, temp)
                newBlock.buildings.append(newBuilding)
        for i in range(len(newBlock.buildings)):
            newBlock.buildings[i].name += vars.BUILDINGNAMES[i]
        self.blocks.append(newBlock)

    def Click(self, aPos):
        for i in range(len(self.blocks)):
            if self.blocks[i].rect.collidepoint(aPos):
                for j in range(len(self.blocks[i].buildings)):
                    for k in range(len(self.blocks[i].buildings[j].rects)):
                        if self.blocks[i].buildings[j].rects[k].collidepoint(aPos):
                            return self.blocks[i].buildings[j]
                for j in range(len(self.blocks[i].emptyPlots)):
                    for k in range(len(self.blocks[i].emptyPlots[j].rects)):
                        if self.blocks[i].emptyPlots[j].rects[k].collidepoint(aPos):
                            return self.blocks[i].emptyPlots[j]
        for i in range(len(self.mapButtons)):
            if self.mapButtons[i].LocCollide(aPos):
                if i == 0:
                    self.showFloors = not self.showFloors
                elif i == 1:
                    self.showSpecial = not self.showSpecial
        return None

    def Draw(self):
        pygame.draw.rect(vars.DISP, vars.BLACK, (0, 0, 900, 900))
        for i in range(len(self.blocks)):
            self.blocks[i].Draw()
        for i in range(len(self.mapButtons)):
            self.mapButtons[i].Draw()


class Block():
    def __init__(self, theLoc):
        self.loc = theLoc
        self.buildings = []
        self.emptyPlots = []
        self.dirty = False              # Do we need to update building demands?
        #column 1 is current levels, column 2 is max levels,
        self.supply = []                # retail, res, parking, office, special
        tempx = (self.loc % 5) * 184
        tempy = int(self.loc / 5) * 184
        self.rect = pygame.Rect(tempx, tempy, 164, 164)

    def Update(self):
        for i in range(len(self.buildings)):
        #TODO: Update buildings Influence by Block
            pass

    def Draw(self):
        pygame.draw.rect(vars.DISP, vars.LTGREY, self.rect)
        for i in range(len(self.buildings)):
            self.buildings[i].Draw()
        for i in range(len(self.emptyPlots)):
            self.emptyPlots[i].Draw()

    def DestroyBuilding(self, buildingIndex):
        destroyed = self.buildings.pop(buildingIndex)
        for i in range(len(destroyed.spaces)):
            temp = Building(self.loc, len(self.emptyPlots),
                            [destroyed.spaces[i]], 'Empty',
                            None, 0, False)
            temp.owner = destroyed.owner
            self.emptyPlots.append(temp)
        return temp

    def AddBuilding(self, index):
        temp = self.emptyPlots.pop(index)
        if len(self.emptyPlots) != 0:
            for i in range(len(self.emptyPlots)-index):
                self.emptyPlots[i+index].index -= 1
        newBuilding = Building(temp.block, len(self.buildings), temp.spaces,
                               'Residential', None, 1)
        newBuilding.owner = temp.owner
        self.buildings.append(newBuilding)
        return newBuilding


class Building():
    def __init__(self, theBlock, theIndex, theSpaces, theType=None,
                 theVal=None, theFloors=None, addFloor=False):
        #Things needed to be initialized
        self.type = theType                 # res, retail, business, gov, park, mega, empty
        self.value = theVal                 # flat sale price of building
        self.floors = theFloors
        self.additionalFloor = addFloor
        self.block = theBlock
        self.index = theIndex
        self.spaces = theSpaces             # number of spaces being taken up on the block
        #Things inferred or defined later
        self.rooms = None                   # number of apts, offices, stores
        self.shape = self.FindShape()
        self.owner = 'The Bank'             # if owner is player or which AI
        self.tenants = []
        self.name = str(self.block + 1)
        self.rects = []
        self.highlight = False
        self.color = vars.BLACK
        self.dirty = False
        self.floorRects = []

        self.Init()

    def Init(self):
        if self.type is None:
            self.ChangeType(vars.BUILDINGTYPES[
                random.randrange(len(vars.BUILDINGTYPES))])
        else:
            self.ChangeType(self.type)
        if self.floors is None:
            self.floors = vars.BUILDINGFLOORS[
                random.randrange(len(vars.BUILDINGFLOORS))]
        if self.value is None:
            self.value = vars.BUILDINGVALUES[
                random.randrange(len(vars.BUILDINGVALUES))]

        self.rooms = 4 * (self.floors + int(self.additionalFloor))

        self.rects = FindLargestRects(self.spaces, self.block)
        if len(self.rects) == 0:
            newRect = pygame.Rect(1, 1, 50, 50)
            newRect.left += (self.block % 5) * 184
            newRect.top += int(self.block / 5) * 184
            newRect.left += (self.spaces[0] % 3) * 56
            newRect.top += int(self.spaces[0] / 3) * 56
            self.rects.append(newRect)

        if self.floors != 0:
            self.floorRects.append(pygame.Rect(self.rects[0].left+1,
                                               self.rects[0].top+1, 5, 5))
            for i in range(self.floors + int(self.additionalFloor)):
                if i != 0:
                    self.floorRects.append(pygame.Rect(self.floorRects[i-1].left,
                                                       self.floorRects[i-1].bottom + 1, 5, 5))

    def Update(self):
        if self.dirty:
            if len(self.floorRects) >= self.floors + int(self.additionalFloor):
                self.floorRects = []
            if not self.floorRects:
                self.floorRects.append(pygame.Rect(self.rects[0].left+1,
                                                   self.rects[0].top+1, 5, 5))
            for i in range(self.floors + int(self.additionalFloor) - len(self.floorRects)):
                self.floorRects.append(pygame.Rect(self.floorRects[i-1].left,
                                                   self.floorRects[i-1].bottom + 1, 5, 5))
            print(len(self.floorRects))
            self.ChangeType(self.type)

    def ChangeType(self, newType):
        self.type = newType
        if self.type == 'Residential':
            self.color = vars.GREEN
        elif self.type == 'Retail' or self.type == 'Special':
            self.color = vars.YELLOW
        elif self.type == 'Office':
            self.color = vars.BLUE
        elif self.type == 'Parking':
            self.color = vars.BLACK
        elif self.type == 'Empty':
            self.color = vars.LTGREY
        else:
            self.color = vars.RED
            print('Error E02: Building Type not appropriately setup')

    def FindShape(self):
        if len(self.spaces) == 1:
            return 'single'
        if not SpacesConnected(self.spaces):
            print('Error D03: Map Data is not properly configured')
            Terminate()
        elif len(self.spaces) == 2:
            return 'double'
        elif len(self.spaces) == 3:
            return 'corner'
        else:
            return 'mega'

    def Draw(self):
        if self.highlight:
            for i in range(len(self.rects)):
                pygame.draw.rect(vars.DISP, vars.BTRED,
                                 (self.rects[i].inflate(10, 10)))
        for i in range(len(self.rects)):
            pygame.draw.rect(vars.DISP, self.color, (self.rects[i]))
        if theMap.showFloors:
            for i in range(len(self.floorRects)):
                pygame.draw.rect(vars.DISP, vars.WHITE, (self.floorRects[i]))
        if theMap.showSpecial and self.type == 'Special':
            pygame.draw.circle(vars.DISP, vars.BLACK,
                               (self.rects[0].right-5, self.rects[0].top+5), 4)


class BuildingType():       # NOT USED YET
    def __init__(self):
        self.type = None


class Tenant():             # NOT USED YET
    def __init__(self):
        self.name = None
        self.occupation = None
        self.credit = None
        self.speech = None
        self.damage = None
        self.renting = []
        self.income = 0


class Owner():
    def __init__(self):
        self.name = None
        self.properties = None  # NEEDS TO BE WRITTEN
        self.income = None      # Maybe
        self.debt = None        # Could be a separate resource
        self.creditLine = None
        self.cash = None
        self.isPlayer = False
        self.playerText = []
        self.dirty = False

    def DrawPlayer(self):
        for i in range(len(self.playerText)):
            self.playerText[i].Draw()

    def Starting(self):
        self.debt = 1000
        self.creditLine = 10000
        self.cash = 40000
        self.isPlayer = True
        self.playerText.append(vars.Text(self.name, None, 48, vars.WHITE, vars.VDKGREY))
        self.playerText.append(vars.Text('  Debt / Credit ', None, 32, vars.WHITE, vars.VDKGREY))
        self.playerText.append(vars.Text(' $ ' + str(self.debt) +
                                         ' / ' + str(self.creditLine), None, 32, vars.WHITE, vars.VDKGREY))
        self.playerText.append(vars.Text('  Cash ', None, 32, vars.WHITE, vars.VDKGREY))
        self.playerText.append(vars.Text(' $ ' + str(self.cash), None, 32, vars.WHITE, vars.VDKGREY))
        self.playerText[0].rect.topleft = (vars.INFOX + 10, vars.INFOY + 10)
        for i in range(len(self.playerText)):
            if i != 0:
                self.playerText[i].rect.topleft = self.playerText[i-1].rect.bottomleft

    def Update(self):
        if self.dirty:
            self.playerText[0] = (vars.Text(self.name, None, 48))
            self.playerText[1] = (vars.Text('  Debt / Credit ', None, 32))
            self.playerText[2] = (vars.Text(' $ ' + str(self.debt) +
                                            ' / ' + str(self.creditLine), None, 32))
            self.playerText[3] = (vars.Text('  Cash ', None, 32))
            self.playerText[4] = (vars.Text(' $ ' + str(self.cash), None, 32))
            self.playerText[0].rect.topleft = (vars.INFOX + 10, vars.INFOY + 10)
            for i in range(len(self.playerText)):
                if i != 0:
                    self.playerText[i].rect.topleft = self.playerText[i-1].rect.bottomleft
            self.dirty = False

    def Draw(self, aPos):
        pass


def SpacesConnected(theSpaces):
    #Check to make sure every space has one next to it
    for i in range(len(theSpaces)):
        connected = False
        for j in range(len(theSpaces)):
            temp = theSpaces[j]-theSpaces[i]
            if abs(temp) == 1 or abs(temp) == 3:
                connected = True
                break
        if not connected:
            return False
    #Check to make sure that if 4, 5 or 6 spaces that not disjointed
    #Does this by ensuring middle row/column not completely empty
    if 3 < len(theSpaces) < 7:
        if 1 not in theSpaces and 4 not in theSpaces and 7 not in theSpaces:
            print('gotcha')
            return False
        if 3 not in theSpaces and 4 not in theSpaces and 5 not in theSpaces:
            return False
    return True


def FindLargestRects(spaces, theBlock):
    farLeft = (theBlock % 5) * 184
    farTop = int(theBlock / 5) * 184

    rects = []
    retVal = []
    #First Break down into every possible group of 2
    couples = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
               [pygame.Rect(1, 1, 106, 50), pygame.Rect(57, 1, 106, 50),
                pygame.Rect(1, 57, 106, 50), pygame.Rect(57, 57, 106, 50),
                pygame.Rect(1, 113, 106, 50), pygame.Rect(57, 113, 106, 50),
                pygame.Rect(1, 1, 50, 106), pygame.Rect(57, 1, 50, 106),
                pygame.Rect(113, 1, 50, 106), pygame.Rect(1, 57, 50, 106),
                pygame.Rect(57, 57, 50, 106), pygame.Rect(113, 57, 50, 106)]]

    if 0 in spaces and 1 in spaces:
        couples[0][0] = 1
    if 2 in spaces and 1 in spaces:
        couples[0][1] = 1
    if 3 in spaces and 4 in spaces:
        couples[0][2] = 1
    if 4 in spaces and 5 in spaces:
        couples[0][3] = 1
    if 6 in spaces and 7 in spaces:
        couples[0][4] = 1
    if 7 in spaces and 8 in spaces:
        couples[0][5] = 1
    if 0 in spaces and 3 in spaces:
        couples[0][6] = 1
    if 4 in spaces and 1 in spaces:
        couples[0][7] = 1
    if 2 in spaces and 5 in spaces:
        couples[0][8] = 1
    if 3 in spaces and 6 in spaces:
        couples[0][9] = 1
    if 4 in spaces and 7 in spaces:
        couples[0][10] = 1
    if 5 in spaces and 8 in spaces:
        couples[0][11] = 1
    
    if 0 not in couples[0]:
        return [pygame.Rect(1, 1, 162, 162)]
    if couples[0][6] and couples[0][7] and couples[0][8]:
        retVal.append('tophalf')
        rects.append(pygame.Rect(1, 1, 162, 106))
        couples[1][6] = 1
        couples[1][7] = 1
        couples[1][8] = 1
    else:
        if couples[0][6] and couples[0][7]:
            retVal.append('topleft')
            rects.append(pygame.Rect(1, 1, 106, 106))
            couples[1][6] = 1
            couples[1][7] = 1
        elif couples[0][7] and couples[0][8]:
            retVal.append('topright')
            rects.append(pygame.Rect(57, 1, 106, 106))
            couples[1][8] = 1
            couples[1][7] = 1
        if couples[0][0] and couples[0][1]:
            retVal.append('top')
            rects.append(pygame.Rect(1, 1, 162, 50))
            couples[1][0] = 1
            couples[1][1] = 1
        if couples[0][2] and couples[0][3]:
            retVal.append('centerh')
            rects.append(pygame.Rect(1, 57, 162, 50))
            couples[1][2] = 1
            couples[1][3] = 1
    if couples[0][9] and couples[0][10] and couples[0][11]:
        retVal.append('bothalf')
        rects.append(pygame.Rect(1, 57, 162, 106))
        couples[1][9] = 1
        couples[1][10] = 1
        couples[1][11] = 1
    else:
        if couples[0][9] and couples[0][10]:
            retVal.append('botleft')
            rects.append(pygame.Rect(1, 57, 106, 106))
            couples[1][9] = 1
            couples[1][10] = 1
        elif couples[0][10] and couples[0][11]:
            retVal.append('botright')
            rects.append(pygame.Rect(57, 57, 106, 106))
            couples[1][10] = 1
            couples[1][11] = 1
        if couples[0][4] and couples[0][5]:
            retVal.append('bot')
            rects.append(pygame.Rect(1, 113, 162, 50))
            couples[1][4] = 1
            couples[1][5] = 1
    if couples[0][0] and couples[0][2] and couples[0][4]:
        retVal.append('lefthalf')
        rects.append(pygame.Rect(1, 1, 106, 162))
        couples[1][0] = 1
        couples[1][2] = 1
        couples[1][4] = 1
    else:
        if couples[0][6] and couples[0][9]:
            retVal.append('left')
            rects.append(pygame.Rect(1, 1, 50, 162))
            couples[1][6] = 1
            couples[1][9] = 1
        if couples[0][7] and couples[0][10]:
            retVal.append('centerv')
            rects.append(pygame.Rect(57, 1, 50, 162))
            couples[1][10] = 1
            couples[1][7] = 1
    if couples[0][1] and couples[0][3] and couples[0][5]:
        retVal.append('righthalf')
        rects.append(pygame.Rect(57, 1, 106, 162))
        couples[1][1] = 1
        couples[1][3] = 1
        couples[1][5] = 1
    else:
        if couples[0][8] and couples[0][11]:
            retVal.append('right')
            rects.append(pygame.Rect(113, 1, 50, 162))
            couples[1][8] = 1
            couples[1][11] = 1

    for i in range(len(couples[0])):
        if couples[0][i] == 1 and couples[1][i] == 0:
            rects.append(couples[2][i])
    for i in range(len(rects)):
        rects[i].left += farLeft
        rects[i].top += farTop
    return rects


def Terminate():
    pygame.quit()
    sys.exit()