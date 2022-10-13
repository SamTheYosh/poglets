import pygame
from random import randint
from math import ceil, floor
import time
pygame.init()

width, height = 800, 800
screen = pygame.display.set_mode((width,height))
pygame.display.set_caption("Poglets")

clock = pygame.time.Clock()

masterVolume = 0.5

class BgBlob:
    def __init__(self,position,farBack):
        self.position = position
        self.farBack = farBack
        global screen
        self.screen = screen
        self.size = randint(50,100)
        self.size = self.size*(self.farBack/100)
        self.surface = pygame.Surface((self.size*2,self.size*2))
        pygame.draw.circle(self.surface, (3*(self.farBack/100),1.5*(self.farBack/100),1.5*(self.farBack/100)), (self.size,self.size), self.size*(self.farBack/100))

    def draw(self):
        self.screen.blit(self.surface, self.position-(self.size*2,self.size*2), special_flags = pygame.BLEND_RGB_ADD)

    def move(self,by):
        self.position += by*(self.farBack/100)*1
        self.position.x = self.position.x%(screen.get_width()+self.size*2)
        self.position.y = self.position.y%(screen.get_height()+self.size*2)

class Text:
    def __init__(self,string,size,position,font,group=0):
        global screen
        self.screen = screen
        
        self.string = string
        self.size = size
        self.position = position
        
        self.font = pygame.font.Font(font,self.size)
        self.surface = None
        self.rect = None

        self.group = group

    def draw(self,string=None,position=None,offset=0,colour=(220,230,240)):
        alpha = 255
        if self.group == 1: alpha = titleTimer
        elif self.group == 0: alpha = 255-titleTimer

        if alpha != 0:
            if position == None: position = self.position
            if string == None: string = self.string
            
            self.surface = self.font.render(string,True,colour)
            self.rect = self.surface.get_rect()
            if offset == 1: self.rect.topleft = position
            elif offset == 2: self.rect.topright = position
            elif offset == 3: self.rect.bottomleft = position
            elif offset == 4: self.rect.center = position
            else: self.rect.center = position
            self.surface.set_alpha(alpha)
            
            self.screen.blit(self.surface,self.rect)

class Poglet:
    def __init__(self,position=None):
        global screen, nameList1, nameList2, camera, width, height
        self.screen = screen
        self.camera = camera
        
        if position == None: self.position = pygame.math.Vector2(randint(int(-width*0.5),int(width*1.5)),randint(int(-height*0.5),int(height*1.5)))
        else: self.position = position
        self.sight = randint(100,300)
        self.hungercap = randint(10,30)
        self.hunger = self.hungercap
        self.aggression = randint(0,10)

        self.name = nameList1[randint(0,len(nameList1)-1)] + nameList2[randint(0,len(nameList2)-1)]
        self.nameLabel = Text(self.name,10,self.position,"FiraMono-Bold.ttf")
        self.statsLabel = Text("Error",15,self.position,"FiraMono-Bold.ttf")
        
        self.colour = None
        self.generateColour()
        self.size = None
        self.generateSize()

        self.velocity = pygame.math.Vector2(0,0)
        self.agility = randint(5,20)/1000

        self.attackTimer = 0

        self.randomDir = randint(0,360)

        self.friends = []

        self.timeAlive = 0
        self.startTime = time.time()

        self.special = False

    def generateColour(self):
        self.colour = ((100*(self.hunger/self.hungercap))+100,200,150)

    def generateSize(self):
        # Make poglet smaller as it gets hungrier
        self.size = ceil(10*(self.hunger/30))

    def drawSelf(self):
        global width,height
        position = self.camera.position - self.position
        if position.x>-10 and position.x<width+10 and position.y>-10 and position.y<height+10:
            self.generateColour()
            self.generateSize()
            pygame.draw.circle(self.screen, self.colour, self.camera.position-self.position, self.size)

    def drawName(self):
        global targetPoglet, target, poglets
        self.timeAlive = time.time()-self.startTime
        if not self.special and self.timeAlive >= 1000:
            self.special = True
            playSound("special", 0.1, self.position)
        position = self.camera.position - self.position
        if self.special: colour=(240, 210, 30)
        else: colour=(220,230,240)
        if position.x>-10 and position.x<width+10 and position.y>-10 and position.y<height+10:
            self.nameLabel.draw(position=(self.camera.position-self.position)-(0,self.size+10),colour=colour)
        if targetPoglet == self:
            self.statsLabel.draw(str(target+1)+". "+self.name,pygame.math.Vector2(10,10),1,colour=colour)
            self.statsLabel.draw(" "*(len(str(target+1))+2)+"Aggression: "+str(self.aggression),pygame.math.Vector2(10,30),1)
            self.statsLabel.draw(" "*(len(str(target+1))+2)+"Agility: "+str(int(self.agility*1000)),pygame.math.Vector2(10,50),1)
            self.statsLabel.draw(" "*(len(str(target+1))+2)+"HP: "+str(ceil(self.hunger))+"/"+str(self.hungercap),pygame.math.Vector2(10,70),1)
            self.statsLabel.draw(str(len(poglets))+" poglets",pygame.math.Vector2(width-10,10),2)
            self.statsLabel.draw("Born "+str(floor(self.timeAlive))+" seconds ago",pygame.math.Vector2(10,height-10),3,colour=colour)

    def drawSight(self):
        pygame.draw.circle(self.screen, (43,33,33), self.camera.position-self.position, self.sight)

    def move(self,by):
        if self.velocity.x<by.x: self.velocity.x+=self.agility
        elif self.velocity.x>by.x: self.velocity.x-=self.agility
        if self.velocity.y<by.y: self.velocity.y+=self.agility
        elif self.velocity.y>by.y: self.velocity.y-=self.agility
        self.position = self.position + self.velocity

        # Can't thiink of any way of doing this without the horrible overlapping
        #volume = self.velocity.length()/10
        #if volume < 1.0: volume = 1.0
        #volume *= 0.3
        #playSound("move"+str(randint(1,6)), volume, self.position)

    def doMovement(self):
        global poglets, food

        toDelete = []
        for i in range(len(self.friends)):
            if self.friends[i][1]>0: self.friends[i][1] -= 1
            else: toDelete.append(self.friends[i])
        self.friends = [x for x in self.friends if not x in toDelete]
        
        self.randomDir += randint(-90,90)
        move = pygame.math.Vector2(1,0).rotate(self.randomDir)
        self.move(move)

        distances = []
        for i in food:
            distance = self.position.distance_to(i.position)-i.value
            if distance <= self.sight: # Can I see any food?
                if i.value == 6: distances.append((0,i))
                else: distances.append((distance,i))

            if distance <= self.size:
                self.heal(i.value)
                if i.value == 6:
                    toAdd.append(Poglet(self.position).inheritGenes(self))
                    self.friends.append([toAdd[-1],5000])
                    playSound("reproduce", 0.1, self.position)
                i.delete()
                playSound("eat"+str(randint(1,3)), 0.1, self.position)

        if distances != []:
            i = min(distances, key=lambda x: x[0])
            move = i[1].position-self.position
            try: move.normalize_ip()
            except ValueError:  move.update(0,0)
            self.move(move)
            
        for poglet in poglets:
            if poglet != self:
                if not poglet in map(lambda x: x[0], self.friends):
                    if self.position.distance_to(poglet.position)-poglet.size <= self.sight: # Can I see any other Poglets?
                        if self.aggression > poglet.aggression:
                            move = poglet.position-self.position
                            try: move.normalize_ip()
                            except ValueError:  move.update(0,0)
                            self.move(move)
                        elif self.aggression <= poglet.aggression:
                            move = self.position-poglet.position
                            try: move.normalize_ip()
                            except ValueError:  move.update(0,0)
                            self.move(move)

                    if self.position.distance_to(poglet.position)-poglet.size <= self.size:
                        if self.attackTimer == 0:
                            self.attackTimer = 30
                            poglet.hurt(1)
                            playSound("attack"+str(randint(1,3)), 0.03, self.position)
                    if self.attackTimer > 0: self.attackTimer -= 1

        if self.hunger <= 0:
            playSound("die", 0.2, self.position)
            self.delete()

        self.hurt(0.02)

    def hurt(self,by):
        self.hunger -= by

    def heal(self,by):
        global toAdd
        self.hunger += by
        if self.hunger>self.hungercap: self.hunger = int(self.hungercap)

    def delete(self):
        global toDelete
        toDelete.append(self)

    def inheritGenes(self,poglet):
        self.sight = poglet.sight+randint(-20,20)
        if self.sight>300: self.sight = 300
        elif self.sight<100: self.sight = 100

        self.hungercap = poglet.hungercap+randint(-5,5)
        if self.hungercap>30: self.hungercap = 30
        elif self.hungercap<10: self.hungercap = 10
        self.hunger = int(self.hungercap)

        self.aggression = poglet.aggression+randint(-2,2)
        if self.aggression>10: self.aggression = 10
        elif self.aggression<0: self.aggression = 0

        self.agility = poglet.aggression+(randint(-3,3)/1000)
        if self.agility>0.02: self.agility = 0.02
        elif self.agility<0.005: self.agility = 0.005

        self.friends.append([poglet,5000])

        return self

class Food:
    def __init__(self,position=None):
        global camera, screen, width, height
        self.camera = camera
        self.screen = screen
        
        if position == None: self.position = pygame.math.Vector2(randint(-width,width*2),randint(-height,height*2))
        else: self.position = position
        self.colour = (randint(0,50),randint(100,200),randint(0,50))
        self.darkerColour = list(self.colour)
        self.darkerColour[0] = 100
        self.value = randint(1,50)/10

        if randint(0,120) == 0:
            self.value = 6
            self.colour = (200,210,100)

        self.appearingCounter = 0

    def draw(self):
        position = self.camera.position - self.position
        if self.appearingCounter<10: self.appearingCounter+=1
        if position.x>-10 and position.x<width+10 and position.y>-10 and position.y<height+10:
            size = self.value*(self.appearingCounter/10)
            if size < 1:
                size = 1
                colour =  self.darkerColour
            else:
                colour = self.colour
            pygame.draw.circle(self.screen, colour, self.camera.position-self.position, size)

    def delete(self):
        global toDelete
        toDelete.append(self)

class Camera:
    def __init__(self,position):
        self.position = position
        self.goTo = position

    def setPos(self,position):
        self.goTo.update(position)

    def update(self):
        self.position = self.position.lerp(self.goTo,0.1)

    def move(self,by):
        self.goTo = self.goTo + by

soundsDict = {}
maxSoundDistance = (min((width, height))*0.5)**2

def playSound(filename, volume=1.0, position=None):
    if not filename in soundsDict:
        soundsDict[filename] = pygame.mixer.Sound("sounds//"+filename+".ogg")

    if position == None:
        sound = pygame.mixer.Sound(soundsDict[filename])
        sound.set_volume(volume*masterVolume)
        sound.play()

    else:
        distance = camera.position.distance_squared_to(position+(screen.get_width()//2,screen.get_height()//2))
        if distance < maxSoundDistance:
            sound = pygame.mixer.Sound(soundsDict[filename])
            channel = pygame.mixer.find_channel()

            if channel != None:
                pan = (camera.position - (position+(screen.get_width()//2,screen.get_height()//2))).x
                if pan < 0:
                    channel.set_volume(1.0,1-((pan**2)/maxSoundDistance))
                else:
                    channel.set_volume(1-((pan**2)/maxSoundDistance),1.0)
                
                sound.set_volume(volume*masterVolume*(1-(distance/maxSoundDistance)))
                channel.play(sound)

titleTimer = 255
titleLabel = Text("Poglets",120,pygame.math.Vector2(width/2,height/2),"FiraMono-Bold.ttf",1)

nameList1 = ["Pog","Bog","Gob","Gog","Bop","Gop","Gonk","Ponk","Pop","Bob","Puck","Buck","Guck","Po","Bo","Go"]
nameList2 = ["gule","ule","er","ger","per","pher","ler","a","pog","geroo","les","ara","io","fle","o","ongi","ta"]

camera = Camera(pygame.math.Vector2(0,0))

toDelete = []
toAdd = []

food = []
for i in range(1000):
    food.append(Food())

poglets = []
for i in range(20):
    poglets.append(Poglet())

target = 0
targetPoglet = poglets[target]
alreadyPressed = []

oldPosition = camera.position.rotate(0)

bgblobs = []
for i in range(40):
    bgblobs.append(BgBlob(pygame.math.Vector2(randint(0,width),randint(0,height)),randint(30,100)))
bgblobs.sort(key=lambda x: x.farBack)

pygame.mixer.music.load("sounds//ambience.ogg")
pygame.mixer.music.set_volume(0.2*masterVolume)
pygame.mixer.music.play(loops=-1, fade_ms=12000)
pygame.time.set_timer(pygame.USEREVENT, 5000, True)
playSound("opening", 1.0)

running = True
while running:
    screen.fill((40,30,30))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.USEREVENT:
            titleTimer -= 1

    if titleTimer < 255 and titleTimer > 0:
        titleTimer -= 2
        if titleTimer < 0: titleTimer = 0

    if pygame.key.get_pressed()[pygame.K_UP]:
        if not pygame.K_UP in alreadyPressed:
            target = (target+1)%len(poglets)
            targetPoglet = poglets[target]
            alreadyPressed.append(pygame.K_UP)
    elif pygame.K_UP in alreadyPressed: alreadyPressed.remove(pygame.K_UP)
    
    if pygame.key.get_pressed()[pygame.K_DOWN]:
        if not pygame.K_DOWN in alreadyPressed:
            target = (target-1)%len(poglets)
            targetPoglet = poglets[target]
            alreadyPressed.append(pygame.K_DOWN)
    elif pygame.K_DOWN in alreadyPressed: alreadyPressed.remove(pygame.K_DOWN)

    while len(food)<1000:
        food.append(Food())
    
    for poglet in poglets:
        poglet.doMovement()

    if toDelete != []:
        poglets = [x for x in poglets if not x in toDelete]
        if poglets == []:
            running = False
            break
        elif targetPoglet in poglets: target = poglets.index(targetPoglet)
        else:
            target = target%len(poglets)
            targetPoglet = poglets[target]
        food = [x for x in food if not x in toDelete]
        toDelete = []
    while toAdd != []: poglets.append(toAdd.pop(0))

    camera.setPos(poglets[target].position+(screen.get_width()//2,screen.get_height()//2))
    camera.update()
    
    poglets[target].drawSight()
    
    for bgblob in bgblobs:
        bgblob.move(camera.position-oldPosition)
        bgblob.draw()
    oldPosition = camera.position.rotate(0)
    
    for i in food:
        i.draw()
    for poglet in sorted(poglets, key=lambda x: x.size):
        poglet.drawSelf()
    for poglet in poglets:
        poglet.drawName()

    titleLabel.draw(offset=4)

    pygame.display.update()
    clock.tick(60)
pygame.quit()
