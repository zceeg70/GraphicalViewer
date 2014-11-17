import pygame as pygame
#import time
import json
import os.path
import csv
import sys
import random

pygame.init()
white = 255,255,255

class ConfigClass:
    def __init__(self):
        self.loadConfig()

    def extract(self,configDict):
        self.squareSize = configDict["squareSize"]
        self.colourSteps = configDict["colourSteps"]
        self.colourEnabled = configDict["colourEnabled"]
        self.CSVFilename = configDict["CSV_to_load"]
        measurementDetails = configDict["details"]
        self.boards = measurementDetails[0]
        self.rpboard = measurementDetails[1]
        self.dimensions = configDict["dimensions"]
        self.offset = configDict["offset"]
    
    def loadConfig(self):
        configFileName = "GraphicalViewerConfig.txt"
        if not os.path.isfile(configFileName):
            print("No config file found. Expected %s"%(configFileName))
            sys.exit()
        configuration = open(configFileName,'r').read()
        configDict = json.loads(configuration)
        self.extract(configDict)
        
        #
        #configuration = ConfigClass()
        #configuration.extract(configDict)
        #return configuration

class CSVLoader:
    def __init__(self,filename,callback=None):
        if not os.path.isfile(filename):
            print("CSV File %s not found"%(filename))
            sys.exit()
        data = []
        headers = []
        self.filename = filename
        self.callback = callback
        self.getHeaders()

    def getHeaders(self):
        filename = self.filename
        with open(filename,"r") as csvfile:
            datareader = csv.reader(csvfile)
            inputRow = []
            for row in datareader:
                headers = row
                break
        self.headers = headers
        self.headersToIndexs()
        return headers

    def getData(self):
        filename = self.filename
        data = []
        with open(filename,"r") as csvfile:
            datareader = csv.reader(csvfile)
            for row in datareader:
                data.append(row)
        self.headersToIndexs()
        breakPoints = self.breakPoints
        rowMax,rowMin = 0,0
        rowMaxMin = []
        dataMax = 0
        dataMin = 400 # Take this from a config?
        sdRowMax,sdRowMin = 0,0
        sdDataMax = 0
        sdDataMin = 400
        #print(breakPoints)
        for index, row in enumerate(data):
            rowMax,rowMin = 0,400
            sdRowMax,sdRowMin = 0,400
            #print(rowMax,rowMin,sdRowMax,sdRowMin,index)
            
            if index == 0: continue
            row[1:] = [float(i) for i in row[1:]]
            
            rowMax = max(row[1:breakPoints[1]])
            rowMin = min(row[1:breakPoints[1]])
            
            
            if dataMin > rowMin: dataMin = rowMin
            if dataMax < rowMax: dataMax = rowMax
            
            sdRowMax = max(row[breakPoints[1]:])
            sdRowMin = min(row[breakPoints[1]:])
            #print(rowMax,rowMin,sdRowMax,sdRowMin)
            rowMaxMin.append([rowMax,rowMin,sdRowMax,sdRowMin])
            if sdDataMin > sdRowMin: sdDataMin = sdRowMin
            if sdDataMax < sdRowMax: sdDataMax = sdRowMax
            #sys.exit()
       # print(dataMax,dataMin,sdDataMax,sdDataMin)
        dataMaxMin = [dataMax,dataMin,sdDataMax,sdDataMin]
       # print(rowMaxMin)
        self.dataMaxMin = dataMaxMin
        self.rowMaxMin = rowMaxMin
        return data,dataMaxMin,rowMaxMin

    def headersToIndexs(self): # Looks for the value "1" in header
        # which should occur twice.
        # breakpoints are the column values
        headers = self.headers
        print(headers)
        breakPoints = []
        for indexH, header in enumerate(headers):
            if indexH == 0: continue
            tokens = header.split(" ")
            if tokens[1] is "1":
                breakPoints.append(indexH)
        self.breakPoints = breakPoints
            
    def getFoldedRow(self):
        filename = self.filename
        breakPoints = self.breakPoints
        # breakpoints found via self.headersToIndexs
        pointRange = breakPoints[1] - breakPoints[0] -1 
        
        foldedRow = [] # First list is timestamp, 2nd Av, 3rd Sd
        with open(filename,"r") as csvfile:
            datareader = csv.reader(csvfile)
            for index, row in enumerate(datareader):
                if index == 0: continue
                else:
                    foldedRow.append([row[0]])
                    #print(row)
                    for x in range(breakPoints[0],breakPoints[1]):
                        foldedRow.append([row[x],row[x+pointRange]])
                    break
        #print foldedRow
        return foldedRow
                
                
                
    def getColumnByHeader(self,header):
        filename = self.filename
        indexHeader = self.headers.index(header)
        with open(filename,"r") as csvfile:
            datareader = csv.reader(csvfile)
            inputColumn = []
            for index,row in enumerate(datareader):
                inputColumn.append(row[indexHeader])

        return inputColumn

class DisplayClass:
    def __init__(self,Configuration,EventsCallback = None):
        self.Configuration = Configuration

    def setup(self):
        Configuration = self.Configuration
        width = Configuration.dimensions[0]
        height = Configuration.dimensions[1]
        size = width, height
        screen = pygame.display.set_mode(size)
        screen.fill(white)
        self.screen = screen
        self.size = size
        myfont = pygame.font.SysFont("monospace",15,bold=True)
        label = myfont.render("TOP LEFT",1,(200,0,0))
        label2 = myfont.render("COLUMNS = BOARDS",1,(200,0,0))
        screen.blit(label,(5,15))
        screen.blit(label2,(95,15))
        #screen.blit()

    def redraw(self):
        screen = self.screen
        screen.fill(white)
        myfont = pygame.font.SysFont("monospace",15,bold=True)
        label = myfont.render("TOP LEFT",1,(200,0,0))
        label2 = myfont.render("COLUMNS = BOARDS",1,(200,0,0))
        screen.blit(label,(5,15))
        screen.blit(label2,(95,15))
        
    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

    def update(self,string, oList,label = "blank"):
        screen = self.screen
        myfont = pygame.font.SysFont("monospace",15,bold=True)
        self.redraw()
        if string is "squares":
            maxSize = self.Configuration.squareSize
            title = myfont.render(label,1,(200,0,0))
            firstSquarePos = oList[0][0].position
            for squareRow in oList:
                for square in squareRow:
                    position = square.position
                    colour = square.colour
                    size = square.size
                    position = [position[0]-(size/2),position[1]-(size/2),size,size]
                    #print(position)
                    pygame.draw.rect(screen,colour,position,0)
            #titlePos  = firstSquarePos[0]
            titlePos = [firstSquarePos[0]-maxSize,firstSquarePos[1]-maxSize]
            screen.blit(title,titlePos)

        
    
class UpdateClass:
    #Data = []
    def __init__(self,Configuration,Display,CSV):
        self.CSV = CSV
        self.Configuration = Configuration
        boards = Configuration.boards
        self.boards = boards
        receivers = Configuration.rpboard
        self.receivers = receivers
        self.squareList = []
        self.Display = Display # manages what is shown on display
        packedData = CSV.getData()
        squareData = packedData[0]
        self.squareData = squareData
        squareDataMaxMin = packedData[1]
        self.squareDataMaxMin = squareDataMaxMin
        squareDataRowMaxMins = packedData[2]
        self.squareDataRowMaxMins = squareDataRowMaxMins
        print(squareDataMaxMin)
        self.Row = 1
        #self.initSquares()
        #CSV.getFoldedRow()
        print("Update Class Initialized")
        
    def initSquares(self):
        Display = self.Display
        squareList = self.squareList
        receivers = self.receivers
        squareSize = self.Configuration.squareSize # is max square size
        offset = self.Configuration.offset
        boards = self.boards
        #print(boards)
        for indexR in range(0,(receivers)):
            #if indexR == 2:
            #    squareSize = 24
            #else:
            #    squareSize = self.Configuration.squareSize
            new = []
            for indexB in range(0,(boards)):
                Sq = Square(squareSize)
                x = offset + 2*indexB*squareSize
                y = offset + 2*indexR*squareSize
                Sq.position = (x,y)
                #print(Sq.position)
                new.append(Sq)
            squareList.append(new)
                #squareList[board][receiver] = Sq
        self.squareSize = squareSize
        Display.update("squares",squareList)

    def updateSquares(self):
        Display = self.Display
        squareList = self.squareList
        CSV = self.CSV
        
        #Values = CSV.getFoldedRow()
        currentRow = self.squareData[self.Row]
        timeStamp = currentRow[0]
        currentRow = currentRow[1:]
        # Find out how many receivers
        recs = self.receivers * self.boards
        MaxMins = self.squareDataMaxMin
        Range = MaxMins[0] - MaxMins[1]
        rowAsDiff = [i - MaxMins[1] for i in currentRow[0:recs]]
        #print(rowAsDiff)
        #row[1:] = [float(i) for i in row[1:]]
        # set the colours
        currentIndex = 0
        for indexB,board in enumerate(squareList):
            for indexR,rec in enumerate(board):
                recTemp = rowAsDiff[currentIndex]
                #print(recTemp)
                pDiff = recTemp / Range
                Red = pDiff * 200
                Blue = (1-pDiff)*200
                rec.colour = (Red,0,Blue)
                #print(rec.colour)
                currentIndex += 1
        # Adjust size to be inversley proportional to sd
        currentIndex = 0
        squareSize = self.squareSize
        Range = MaxMins[2] - MaxMins[3]
        rowAsDiff = [i - MaxMins[3] for i in currentRow[recs:]]
        for indexB,board in enumerate(squareList):
            for indexR,rec in enumerate(board):
                recSd = rowAsDiff[currentIndex]
                #print(recSd)
                pDiff = recSd / Range
                rec.size = squareSize * (1-pDiff)
                #print(rec.size)
                currentIndex += 1
        
                #Red = recTemp
                #print(rec.colour)
        

        # set the size

        
        Display.update("squares",squareList,(str(self.Row)+":"+timeStamp))
        self.Row += 1
        if self.Row == len(self.squareData): self.Row = 1
        
class Square:
    def __init__(self,size):
        self.position = [0,0]
        self.size = size
        self.colour = [0,0,0]
        self.heat = 0
    
def main():
    Configuration = ConfigClass()
    CSV = CSVLoader(Configuration.CSVFilename)
    
    Display = DisplayClass(Configuration)
    Update = UpdateClass(Configuration,Display,CSV)
    Display.setup()
    Update.initSquares()
    #print(CSV.headers)
    #Squares
    running = True
    while running:
        pygame.display.flip()
        pygame.time.delay(900)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        Update.updateSquares()
    pygame.quit()
    
if __name__ == "__main__":
    try:
        main()
    except:
        pygame.quit()
        raise

