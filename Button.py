import pygame
class Button(pygame.sprite.Sprite):
    'used to make buttons'
    def __init__(self,label="Button",position=(600,150),size=(40,120),sub = False):
        pygame.sprite.Sprite.__init__(self)
        #x , y  = 600,150
        self.position = position
        x = position[0]
        y = position[1]
        w , h = size[0], size[1]
        self.size = size
##        self.rect = pygame.Rect((x-w),(y-h),20,40)
        self.rect = pygame.Rect((x,y),(h,w))
        self.colour = [174,174,174]
        self.isPressed = False
        self.label = label
        self.sub = sub

    def setCoords(self,x,y):
        self.rect.topleft = x,y

    def toggle(self):
        pressed = not self.isPressed
        
        if pressed:
            self.colour = [130,130,130]
        else:
            self.colour = [174,174,174]
        self.isPressed = pressed

    def unpress(self):
        if self.isPressed == True:
            self.toggle()
            

    def pressed(self,mouse):
        if mouse[0] > self.rect.topleft[0]:
            if mouse[1] > self.rect.topleft[1]:
                if mouse[0] < self.rect.bottomright[0]:
                    if mouse[1] < self.rect.bottomright[1]:
                        #self.toggle()
                        return True
                    else: return False
                else: return False
            else: return False
        else: return False
