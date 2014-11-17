import random
from datetime import date,datetime
import time
import csv

class CSV:
    def __init__(self):
        self.path = "BWTestData.txt"
        pass

    def createCSV(self):
        pass

        
    def writeLine(self,line):
        pass

    def write(self,dataset):
        try:
            csv_file = open(self.path,"w")
            if not(type(dataset) is list): return "Dataset must be a list"
            writer = csv.writer(csv_file,delimiter=',')
            for line in dataset:
                #print(line)
                if type(line) is list: writer.writerow(line)
                else: writer.writerow([line,])
        finally:
            print("Save succesfull")
            csv_file.close()

class LineGen:
    def __init__(self,recs):
        self.recs = recs
        self.boards = 10

    def headerLine(self):
        recs = self.recs
        boards = self.boards
        first = "Timestamp"
        header = []
        header.append(first)
        string = "Ext Temp"
        header.append(string)
        for x in range(0,boards):
            string = "Board"+str(x)+"Temp"
            header.append(string)
        for x in range(0,recs):
            string = "Rx"+str(x)+" Av"
            header.append(string)
        for x in range(0,recs):
            string = "Rx"+str(x)+" SD"
            header.append(string)
        return header
            #print(string)
            
    def newLine(self, temp = "ambient", uncertainty = 0):
        recs = self.recs
        line = []
        line.append(str(self.timeStamp()))
        line.append(19.4) # Ext Temp
        for x in range(0,self.boards):
            line.append(self.boardTemp())
        for x in range(0,recs):
            line.append(self.AVMeas(temp))
        for x in range(0,recs):
            line.append(self.Sd(temp,uncertainty))
        #print(line)
        return line

    def boardTemp(self):
        value = float(random.randrange(190,210)/10)
        return value
        

    def timeStamp(self):
        return datetime.today()

    def AVMeas(self,temp = "ambient"):
        if "ambient" in temp.lower():
            AV = random.randrange(29100,29500,5)
        elif "cold" in temp.lower():
            #print("Im cold")
            AV = random.randrange(24800,25000,5)
        elif "changing" in temp.lower():
            #print("rr")
            AV = random.randrange(24800, 29500,10)
           # print(temperature)
        else:
            return False
        tfloat = float(AV)
        
        #print((tfloat/100))
        return (tfloat/100)

    def Sd(self,temp = "ambient", uncertainty = 0):
        if "ambient" in temp.lower(): # want medium variation
            std = random.randrange(0,4000)
        elif "cold" in temp.lower(): # slightly lower variation
            std = random.randrange(0,2500)
        elif "changing" in temp.lower():
            std = random.randrange(4000,9000,100)
        else:
            return False
        sdfloat = float(std)
        return (sdfloat/100)
        
def main():
    #newLine()
    Generator = LineGen(100)
    CSVFile = CSV()
    genData = []
    headers = Generator.headerLine()
    genData.append(headers)
    for y in xrange(0,3):
        for x in xrange(0,5):
            #print(x)
            line = Generator.newLine("ambient")
            genData.append(line)
        line = Generator.newLine("changing")
        genData.append(line)
        line = Generator.newLine("changing")
        genData.append(line)
        for x in xrange(0,4):
            #print(x)
            line = Generator.newLine("cold")
            genData.append(line)
        line = Generator.newLine("changing")
        genData.append(line)
        for x in xrange(0,3):
            #print(x)
            line = Generator.newLine("ambient")
            genData.append(line)
    for y in xrange(0,10):
        #print(y)
        line = Generator.newLine("ambient")
        genData.append(line)
    #CSVFile.write(genData)
    #print(len(genData))
    #for bit in line:
            #print(type(bit))
     #   print(Generator.newLine())
    
    CSVFile.write(genData)



if __name__ == "__main__":
    main()
