import os.path
import json
import sys

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
