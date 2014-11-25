import os.path
import sys
import csv
import copy

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
        self.data = data

    def splitData(self,removeSet = "None"):
        data = self.data
        breakPoints = sorted(self.breakPoints)
        dataSetsMapping = self.dataSetsMapping
        mappedSets = {}
        sets = len(breakPoints)-1 # number of sets of data
        datasets = []
        maxminSet = []
        for x in range(0,sets):
            newSet = []
            for row in data: # Does it PER ROW
                newSet.append(row[breakPoints[x]:breakPoints[x+1]])
            datasets.append(newSet)
            if type(removeSet) is str:
                maxmin = self.getMaxMin(newSet)
            else:
                #print("Commanded to remove:",removeSet)
                maxmin = self.getMaxMin(newSet,removeSet)
            if type(maxmin) is bool:
                timestamp = newSet
            maxminSet.append(maxmin)
            #print(newSet[0])
        if len(datasets) == len(dataSetsMapping):
            #print("Mapping")
            for dataset,maxmin,mapping in zip(datasets,maxminSet,dataSetsMapping):
                mappedSets[mapping] = {"data":dataset,"maxmin":maxmin}
##                print("Mapping:%s,maxmin:%d"%(dataset,maxmin))
        self.mappedSets = mappedSets
        # At this point script has multiple data sets in its possession, accessible through the header
        # generic name
        
    def getMaxMin(self,datasetToTest,removeSet = "no"):
        dataset = copy.deepcopy(datasetToTest)
        rowMaxList,rowMinList = [],[]
##        removeSet = removeSet
        dataMaxMin = []
        indexMaxMin = []
        indexRowMaxMin = []
        unparseableFlag = False
        for index, row in enumerate(dataset):
            #print(row)
            if 'Timestamp' in row:
                #print("Detected 'Timestamp'")
                unparseableFlag = True
                return False
            if index == 0:
                dataId = row[0]
                #print("first position in row =",dataId)
                continue
            
            if len(row) > 1:
                errorTrack = []
                errorTrack.append(type(removeSet))
                errorTrack.append(removeSet)
                if (not type(removeSet) is str) and (len(row)>max(removeSet)):
                    errorTrack.append(removeSet)
                    removeSet.sort(reverse=True)
                    for removeIndex in removeSet:
                        row.pop(removeIndex)
                
                # Must remain INDEPENDENT of row size
                row = [float(i) for i in row]
                rowMax = max(row)
                rowMin = min(row)
                #print(rowMax,rowMin)
            else:
                row = float(row[0])
                rowMax = row
                rowMin = row
            #indexRowMaxMin.append([dataset.index(row),row.index(rowMax),row.index(rowMin)])
            rowMaxList.append(rowMax)
            rowMinList.append(rowMin)
        
        rowMaxFrom, dataMax = max(
            enumerate(rowMaxList),
            key=lambda x: x[1]
        )
        rowMinFrom, dataMin = min(
            enumerate(rowMinList),
            key=lambda x:x[1]
        )
##        rowMaxFrom += 1
##        rowMinFrom += 1
##        row = dataset[rowMaxFrom]
##        
##        if len(row) > 1:
##            row = [float(i) for i in row]
##            indexFrom = row.index(dataMax)
##            rowMax = max(row)
##        else:
##            row = float(row[0])
##            indexFrom = 0
##            rowMax = row
##        row = dataset[rowMinFrom]
##        row = [float(i) for i in row]
##        minIndexFrom = row.index(dataMin)
        dataMaxMin.append([dataMax,dataMin])
        #print(dataId,dataMaxMin,"Index max",indexFrom,"rowMax",rowMax)
        #print("Index min",minIndexFrom,dataMin)
        
        return dataMaxMin
