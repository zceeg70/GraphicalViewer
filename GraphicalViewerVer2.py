import pygame as pygame
from pygame import mouse
from Button import Button as Button
from Square import Square as Square
from BWConfig import ConfigClass
from BWDisplay import DisplayClass
from CSVReader import CSVLoader
#import time
import json
import os.path
import csv
import sys
import random
import copy

pygame.init()
white = 255,255,255

class UpdateClass:
    #Data = []
    def __init__(self,Configuration,Display,CSV,buttonList):
        # Links to other shared classes
        self.buttonList = buttonList
        self.Configuration = Configuration
        self.CSV = CSV
        self.Display = Display # manages what is shown on display 
        # Unpack configuration datums
        boards = Configuration.boards
        self.boards = boards
        receivers = Configuration.rpboard
        self.receivers = receivers
        # Setup lists which will be updated
        self.squareList = []
        self.excludeList = []
        self.labelList = []
        # Import data
        BWRecData = CSV.mappedSets
        self.BWRecData = BWRecData


        Av = Configuration.squareColourFrom
        if Av not in BWRecData:
            print("Column %s in 'squareColourFrom' does not exist.. exiting"%(Av))
            sys.exit()
        print("Square colour will be calculated from: %s"%(Av))
        self.Av = Av
        self.prepData()

        self.row = 0

        
        print("Update Class Initialized")
        
    def initSquares(self):
        print("initSquares called")
        Display = self.Display
        squareList = self.squareList
        labelList = self.labelList
        receivers = self.receivers
        squareSize = self.Configuration.squareSize # is max square size
        offset = self.Configuration.offset
        boards = self.boards
        squaresNeeded = receivers*boards
        #squareList = []
        for recCount in xrange(0,squaresNeeded):
            Sq = Square(squareSize)
            x = offset + int(recCount%boards)*2*squareSize
            y = offset + int(recCount/boards)*2*squareSize
            Sq.position = (x,y)
            squareList.append(Sq)
        
        self.squareSize = squareSize
        Display.update("squares",squareList)
    
    def initBoardTemps(self):
        Display = self.Display
        labelList = self.labelList
        receivers = self.receivers
        squareSize = self.Configuration.squareSize
        offset=self.Configuration.offset
        boards = self.boards
        squaresNeeded = receivers*boards
        
        yOffset = offset+ receivers*2*squareSize - squareSize
        for boardCount in range(0, boards):
            x = offset + int(boardCount%boards)*2*squareSize -squareSize/2
            Label = label(99,[x,yOffset])
            labelList.append(Label)
        Display.update("squareLabels",labelList)

    def updateTemps(self):
        Display = self.Display
        row = self.row
        temperatureData = self.BWRecData["Board"]["data"][1:]
        labelList = self.labelList
        for indexLab,label in enumerate(labelList):
            label.setValue(temperatureData[row][indexLab])
        Display.update("squareLabels",labelList)
            
        
        
    def prepData(self):
        data = self.BWRecData
        Configuration = self.Configuration
        excludeList = self.excludeList
        #Determine range of readings
        #For 'Av'
        Av = self.Av
        AvMaxMin = data[Av]["maxmin"][0]
        AvRange = AvMaxMin[0] - AvMaxMin[1]
        AvDiff = []
        for row in data[Av]["data"][1:]:
            newRow = []
            newRow = [float(i) - AvMaxMin[1] for i in row]
            AvDiff.append(newRow)
        AvPerc = []
        for row in AvDiff:
            newRow = []
            newRow = [float(i) / AvRange for i in row]
            AvPerc.append(newRow)
        #Result - Av converted into a percentage.
        #print("length AvPerc = %d"%(len(AvPerc)))
        self.AvPerc = AvPerc
        
        #For 'SD'
        Sd = Configuration.squareSizeFrom
        if Sd not in data:
            print("Column %s in 'squareSizeFrom' does not exist.. exiting"%(Av))
        print("Square size will be calculated from: %s"%(Sd))
        SdMaxMin = data[Sd]["maxmin"][0]
        SdRange = SdMaxMin[0] - SdMaxMin[1]
        SdDiff = []
        for row in data[Sd]["data"][1:]:
            newRow = []
            newRow = [float(i) - SdMaxMin[1] for i in row]
            SdDiff.append(newRow)
        SdPerc = []
        for row in SdDiff:
            newRow = []
            newRow = [ 1 - (i / SdRange) for i in row]
            SdPerc.append(newRow)
        #Result 
        self.SdPerc = SdPerc

    def toggleSquare(self,square):
        buttonList = self.buttonList
        delete = True
        for button in buttonList:
            #print(button)
            if button.label == "Toggle":
                if button.isPressed:
                    #print("Toggle button pressed")
                    delete = True
                else:
                    #print("Toggle button not pressed")
                    delete = False        
        
        excludeList = self.excludeList
        squareList = self.squareList
        if not square  in squareList:
            print("square to delete not found")
            return
        
        indexOf = squareList.index(square)
        if not delete:
            print("Removing squre from exclude list")
            excludeList.remove(indexOf)
        else:
            if not indexOf in excludeList:
                excludeList.append(indexOf)
                square.colour = (0,0,0)
                square.size = self.squareSize/2
            else:
                return
        if len(excludeList)>0:
            self.CSV.splitData(excludeList)
            self.BWRecData = self.CSV.mappedSets
            self.prepData()
        else:
            self.CSV.splitData()
            self.BWRecData = self.CSV.mappedSets
            self.prepData()
        
    def updateSquares(self):
        AvPerc = self.AvPerc
        SdPerc = self.SdPerc
        row = self.row

        Display = self.Display
        squareList = self.squareList
        squareSize = self.squareSize
        excludeList = self.excludeList

        for index,square in enumerate(squareList):
            if index in excludeList:
                continue
            Red = AvPerc[row][index] * 255
            Blue = (1-AvPerc[row][index])*200
            square.colour = (Red,0,Blue)
            square.size = squareSize*SdPerc[row][index]
        Timestamp = str(self.BWRecData["Timestamp"]["data"][row+1])
        Display.update("squares",squareList,str(row)+Timestamp)
        self.updateTemps()
        self.row += 1
        if self.row == len(AvPerc): self.row = 1

    def squarePressed(self,pos):
        squareList = self.squareList
        squareSize = self.squareSize*2 # defines the search radius
        difference = []
        for square in squareList:
            sqPos = square.position
            difference = (sqPos[0] - pos[0])**2 + (sqPos[1]-pos[1])**2
            if difference < squareSize:
                return square
        return False
        
class label:
    def __init__(self,value,pos):
        self.myfont = pygame.font.SysFont("monospace",15,bold=True)
        self.pos = pos
        self.setValue(value)
        self.render()

    def render(self):
        self.label = self.myfont.render(self.value,1,(200,0,0))

    def setValue(self,value):
        self.value = str(value)
        self.render()

    

    
def main():
    Configuration = ConfigClass()
    CSV = CSVLoader(Configuration)
    #button = Button()
    buttonList = []
    createButtons = ["Toggle","Reset","Select","Board"]
    buttonState = {"Toggle":False,"Reset":False,"Select":False,"Board":False,
                   "A-On":False,"A-Off":False,"Mode":{"F":0,"T":1}}
    positions = [(600,50),(722,50),(844,50),(966,50)]
    #button.setCoords(500,200)
    for indexButton,newButton in enumerate(createButtons):
        buttonList.append(Button(newButton,positions[indexButton]))
    halfButtons = ["A-On","A-Off"]
    positions = [(844,20),(912,20)]
    for indexButton,halfButton in enumerate(halfButtons):
        buttonList.append(Button(halfButton,positions[indexButton],(25,58),sub=True))

    
    Display = DisplayClass(Configuration,buttonList)
    Update = UpdateClass(Configuration,Display,CSV,buttonList)
    Display.setup()
    Update.initSquares()
    Update.initBoardTemps()

   
    
    running = True
    modeSet = "Info"
    while running:
        #Display.save()
        pygame.display.flip()
        pygame.time.delay(100)
        Display.redraw()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                # On mouse click get the position of the mouse down
                pos = pygame.mouse.get_pos()
                # Find which square (if any) is pressed
                square = Update.squarePressed(pos)
                # Check each button to see if that one is pressed
                for button in buttonList:
                    if button.pressed(pos): 
                        if not button.isPressed: # If not already pressed
                            modeSet = button.label
                        button.toggle() # Change colour 
                        buttonState[button.label] = not buttonState[button.label]
                        # Now turn off the other buttons
                        # Unless those buttons are sub-specifiers to other buttons
                        for b in buttonList:
                            if b == button: continue
                            if not b.isPressed: continue #Not pressed. Ignore
                            if button.sub or b.sub:
                                if button.label is "A-On" and b.label is "A-Off":
                                    b.toggle()
                                elif button.label is "A-Off" and b.label is "A-On":
                                    b.toggle()
                                else: continue
                            buttonState[b.label] = False    
                            b.unpress()
                        if modeSet is "Reset":
                            Update.row = 0
                            button.unpress()
                if not type(square) is bool:
                    if buttonState["Toggle"]:
                        Update.toggleSquare(square)
                        #print(square.position)
                    elif buttonState["Select"]:
                        square.toggleCircle((179,179,179))
                        #print("Select selected, buttonState[A-on]:",buttonState["A-On"])
                        if buttonState['A-On']:
                            for squares in Update.squareList:
                                squares.highlight(colour=(179,179,179))
                        elif buttonState["A-Off"]:
                            for squares in Update.squareList:
                                squares.circleOff()
                        
                    elif modeSet is "Board":
                        pass
                
                
        Update.updateSquares()
    pygame.quit()
    
if __name__ == "__main__":
    try:
        main()
    except:
        pygame.quit()
        raise

