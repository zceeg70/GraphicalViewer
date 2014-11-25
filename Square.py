class Square:
    def __init__(self,size):
        self.position = [0,0]
        self.size = size
        self.colour = [0,0,0]
        self.Av = 0
        self.selected = False
        self.circleOn = False
        self.circleColour = (255,255,255)

    def toggleCircle(self,colour=(255,255,255)):
        circleOn = self.circleOn
        self.circleOn = not self.circleOn
        self.circleColour = colour

    def circleOff(self):
        self.circleOn = False
        self.circleColour = (255,255,255)

    def highlight(self,colour=(174,174,174)):
        self.circleOn = True
        self.circleColour = colour
