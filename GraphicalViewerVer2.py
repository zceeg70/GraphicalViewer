import pygame as pygame
from pygame import mouse
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

    def loadConfig(self):
        configFileName = "GraphicalViewerConfig.txt"
        if not os.path.isfile(configFileName):
            print("No config file found. Expected %s"%(configFileName))
            sys.exit()
        configuration = open(configFileName,'r').read()
        configDict = json.loads(configuration)
        self.extract(configDict)
        
    def extract(self,configDict):
        self.squareSize = configDict["squareSize"]
        self.colourSteps = configDict["colourSteps"]
        self.colourEnabled = configDict["colourEnabled"]
        self.CSVFilename = configDict["CSV_to_load"]
        measurementDetails = configDict["boards|recs"]
        self.boards = measurementDetails[0]
        self.rpboard = measurementDetails[1]
        self.dimensions = configDict["dimensions"]
        self.offset = configDict["offset"]
        self.specCol = configDict["columnsOfInterest"]
        self.squareSizeFrom = configDict["squareSizeFrom"]
        self.squareColourFrom = configDict["squareColourFrom"]

class CSVLoader:
    def __init__(self,Configuration,callback=None):
        filename = Configuration.CSVFilename
        if not os.path.isfile(filename):
            print("CSV File %s not found"%(filename))
            sys.exit()
        data = []
        headers = []
        self.filename = filename
        self.callback = callback
        self.Configuration = Configuration
        self.getHeaders()
        self.getData()
        self.splitData()

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

    def headersToIndexs(self): # Looks for the value "1" in header
        # which should occur twice.
        # breakpoints are the column values
        headers = self.headers
        splitPoints = self.Configuration.specCol #Strings of expected headers
        dataSplitPoints = {}
        breakPoints = []
        headerCount = {}
        for expectedString in splitPoints:
            headerCount[expectedString] = 0
            print("Searching for header: %s"%(expectedString))
            for indexH,header in enumerate(headers):
                #print("Searching for header: %s,found header: %s"%(expectedString,header))
                if expectedString in header:
                    headerCount[expectedString] += 1
                    if not expectedString in dataSplitPoints:
                        dataSplitPoints[expectedString] = indexH
                        breakPoints.append(indexH)
            if headerCount[expectedString] == 0:
                print("Header not found:%s. Update config file. System will exit"%(expectedString))
                sys.exit()
            else:
                print("Found %d occurences of header: %s"%(headerCount[expectedString],expectedString))
                print("     at column: %s"%(dataSplitPoints[expectedString]))
        cumulative = 0
        for item in headerCount:
            cumulative += headerCount[item]
        if cumulative < len(headers):
            print("Some header was not identified in configuration")
        elif cumulative == int(len(headers)):
            print("Number of columns tallys with columns specified in configuration")
        breakPoints.append(len(headers))
        
        dataSets = {}
        dataSets = sorted(dataSplitPoints,key=dataSplitPoints.__getitem__)
        dataSetsMapping = {}
        dataSetsMapping = dataSets
        self.breakPoints = breakPoints
        self.dataSetsMapping = dataSetsMapping
    
    def getData(self):
        filename = self.filename
        data = []
        with open(filename,"r") as csvfile:
            datareader = csv.reader(csvfile)
            for row in datareader:
                data.append(row)
     #   self.headersToIndexs()
     #   breakPoints = self.breakPoints
        
       # rowMaxMin = []
     #   
      #  for index, row in enumerate(data): # Each row in data find max/mins
        #    if index == 0: continue
       #     row[1:] = [float(i) for i in row[1:]]
            
        #    rowMax = max(row[1:breakPoints[1]])
        #    rowMin = min(row[1:breakPoints[1]])

         #   sdRowMax = max(row[breakPoints[1]:])
         #   sdRowMin = min(row[breakPoints[1]:])
            
          #  if index == 1:
          #      dataMin,dataMax = rowMin,rowMax
          #      sdDataMin,sdDataMax = sdRowMin,sdRowMax
          #  else:
          #      if dataMin > rowMin: dataMin = rowMin
          #      if dataMax < rowMax: dataMax = rowMax
          #      if sdDataMin > sdRowMin: sdDataMin = sdRowMin
          #      if sdDataMax < sdRowMax: sdDataMax = sdRowMax
          #  rowMaxMin.append([rowMax,rowMin,sdRowMax,sdRowMin])
            
        #dataMaxMin = [dataMax,dataMin,sdDataMax,sdDataMin]
        #self.dataMaxMin = dataMaxMin
        #self.rowMaxMin = rowMaxMin
        self.data = data
        #return data,dataMaxMin,rowMaxMin

    def splitData(self):
        data = self.data
        breakPoints = sorted(self.breakPoints)
        dataSetsMapping = self.dataSetsMapping
        mappedSets = {}
        sets = len(breakPoints)-1 # number of sets of data
        datasets = []
        maxminSet = []
        for x in range(0,sets):
            newSet = []
            for row in data:
                newSet.append(row[breakPoints[x]:breakPoints[x+1]])
            datasets.append(newSet)
            maxmin = self.getMaxMin(newSet)
            if type(maxmin) is bool:
                timestamp = newSet
            maxminSet.append(maxmin)
            #print(newSet[0])
        if len(datasets) == len(dataSetsMapping):
            print("Mapping")
            for dataset,maxmin,mapping in zip(datasets,maxminSet,dataSetsMapping):
                mappedSets[mapping] = {"data":dataset,"maxmin":maxmin}
        
        #print(mappedSets.keys())
        #print(mappedSets["Timestamp"].keys())
        #print(mappedSets["Timestamp"]["data"])
        #print(mappedSets["Timestamp"])
        self.mappedSets = mappedSets
        # At this point script has multiple data sets in its possession, accessible through the header
        # generic name
        
    def getMaxMin(self,dataset):
        rowMaxList,rowMinList = [],[]
        dataMaxMin = []
        unparseableFlag = False
        for index, row in enumerate(dataset):
            #print(row)
            if 'Timestamp' in row:
                #print("Detected 'Timestamp'")
                unparseableFlag = True
                return False
            if index == 0:
                #print(row)
                continue
            #print(type(row),len(row))
            if len(row) > 1:
                row = [float(i) for i in row[1:]]
                rowMax = max(row)
                rowMin = min(row)
                #print(rowMax,rowMin)
            else:
                row = float(row[0])
                rowMax = row
                rowMin = row
            rowMaxList.append(rowMax)
            rowMinList.append(rowMin)
        #print("rowMaxMin")
        #print(rowMaxMin[0][:])
        dataMax = max(rowMaxList)
        dataMin = min(rowMinList)
        dataMaxMin.append([dataMax,dataMin])
        print(dataMaxMin)
        
        return dataMaxMin

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
##        Configuration = self.Configuration
##        boards = Configuration.boards
##        receivers = Configuration.receivers
        myfont = pygame.font.SysFont("monospace",15,bold=True)
        self.redraw()
        if string is "squares":
            maxSize = self.Configuration.squareSize
            title = myfont.render(label,1,(200,0,0))
##            firstSquarePos = oList[0][0].position
##            for squareRow in oList:
##                for square in squareRow:
##                    position = square.position
##                    colour = square.colour
##                    size = square.size
##                    position = [position[0]-(size/2),position[1]-(size/2),size,size]
##                    #print(position)
##                    pygame.draw.rect(screen,colour,position,0)
##            #titlePos  = firstSquarePos[0]
            firstSquarePos = oList[0].position
            for square in oList:
                position = square.position
                colour = square.colour
                size = square.size
                position = [position[0]-(size/2),position[1]-(size/2),size,size]
                pygame.draw.rect(screen,colour,position,0)
            titlePos = [firstSquarePos[0]-maxSize,firstSquarePos[1]-maxSize]
            screen.blit(title,titlePos)

        
    
class UpdateClass:
    #Data = []
    def __init__(self,Configuration,Display,CSV):
        # Links to other shared classes
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

        # Import data
        BWRecData = CSV.mappedSets
        self.BWRecData = BWRecData

        self.prepData()

        self.row = 0
        print("Update Class Initialized")
        
    def initSquares(self):
        Display = self.Display
        squareList = self.squareList
        receivers = self.receivers
        squareSize = self.Configuration.squareSize # is max square size
        offset = self.Configuration.offset
        boards = self.boards
        squaresNeeded = receivers*boards
        
        for recCount in xrange(0,squaresNeeded):
            Sq = Square(squareSize)
            x = offset + int(recCount%10)*2*squareSize
            y = offset + int(recCount/10)*2*squareSize
            Sq.position = (x,y)
##            print(x,y)
            squareList.append(Sq)
        #print(len(squareList))
##        sys.exit()
                #squareList[board][receiver] = Sq
        self.squareSize = squareSize
        Display.update("squares",squareList)

    def prepData(self):
        data = self.BWRecData
        Configuration = self.Configuration

        #Determine range of readings
        #For 'Av'
        Av = Configuration.squareColourFrom
        if Av not in data:
            print("Column %s in 'squareColourFrom' does not exist.. exiting"%(Av))
            sys.exit()
        print("Square colour will be calculated from: %s"%(Av))
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
        
    def updateSquares(self):
        AvPerc = self.AvPerc
        SdPerc = self.SdPerc
        row = self.row

        Display = self.Display
        squareList = self.squareList
        squareSize = self.squareSize

        currentIndex = 0
##        print(squareList)
        for index,square in enumerate(squareList):
                    
            Red = AvPerc[row][index] * 200
            Blue = (1-AvPerc[row][index])*200
            square.colour = (Red,0,Blue)

            square.size = squareSize*SdPerc[row][index]
            currentIndex += 1
        # Adjust size to be inversley proportional to sd
        currentIndex = 0
        Timestamp = str(self.BWRecData["Timestamp"]["data"][row+1])
        #print(Timestamp)

        
        Display.update("squares",squareList,str(row)+Timestamp)
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
        
class Square:
    def __init__(self,size):
        self.position = [0,0]
        self.size = size
        self.colour = [0,0,0]
        self.Av = 0
    
def main():
    Configuration = ConfigClass()
    CSV = CSVLoader(Configuration)
    
    Display = DisplayClass(Configuration)
    Update = UpdateClass(Configuration,Display,CSV)
    Display.setup()
    Update.initSquares()
    
    running = True
    while running:
        pygame.display.flip()
        pygame.time.delay(100)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                square = Update.squarePressed(pos)
                if not type(square) is bool:
                    print(square.position)
        Update.updateSquares()
    pygame.quit()
    
if __name__ == "__main__":
    try:
        main()
    except:
        pygame.quit()
        raise

