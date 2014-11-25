import pygame
import sys
white = 255,255,255
class DisplayClass:
    def __init__(self,Configuration,Buttons,EventsCallback = None):
        self.Configuration = Configuration
        self.Buttons = Buttons
        self.Count = 0

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
        #self.screen = screen
        #screen.blit()
    def save(self):
        screen = self.screen
        Count = self.Count
        stringCount = str(Count)
        while len(stringCount)<3:
            stringCount = "0"+stringCount
        pygame.image.save(screen,"BWImages\SFBW"+stringCount+".jpeg")
        Count = Count + 1
        self.Count = Count

    def redraw(self):
        screen = self.screen
        screen.fill(white)
        myfont = pygame.font.SysFont("monospace",15,bold=True)
        Buttons = self.Buttons
        for button in Buttons: # Draws all buttons
            s = pygame.Surface((button.size[1],button.size[0]))
            s.fill(button.colour)
            screen.blit(s,(button.position[0],button.position[1]))
            bLabel = myfont.render(button.label,1,(0,255,255))
            bLabelPos = [button.position[0]+(button.size[1]/3),
                         button.position[1]+(button.size[0]/3)]
            screen.blit(bLabel,bLabelPos)
        
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
        #self.redraw()
        if string is "squares":
            maxSize = self.Configuration.squareSize
            title = myfont.render(label,1,(200,0,0))
            firstSquarePos = oList[0].position
            for square in oList:
                position = square.position
                colour = square.colour
                size = square.size
                Rectposition = [position[0]-(size/2),position[1]-(size/2),size,size]
                pygame.draw.rect(screen,colour,Rectposition,0)
                if square.circleOn == True:
                    colour = square.circleColour
                    pygame.draw.circle(screen,colour,[position[0],position[1]],maxSize,3)
##                    pygame.draw.circle(

            titlePos = [firstSquarePos[0]-maxSize,firstSquarePos[1]-maxSize]
            screen.blit(title,titlePos)
        elif string is "squareLabels":
            for o in oList:
                screen.blit(o.label,o.pos)
