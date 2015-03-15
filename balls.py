#!/usr/bin/env python
# coding: utf

import pygame
import random

SIZE = 640, 480
GRAVITY = 0.2

def intn(*arg):
    return map(int,arg)

def Init(sz):
    '''Turn PyGame on'''
    global screen, screenrect
    pygame.init()
    screen = pygame.display.set_mode(sz)
    screenrect = screen.get_rect()

class GameMode:
    '''Basic game mode class'''
    def __init__(self):
        self.background = pygame.Color("black")

    def Events(self,event):
        '''Event parser'''
        pass

    def Draw(self, screen):
        screen.fill(self.background)

    def Logic(self, screen):
        '''What to calculate'''
        pass

    def Leave(self):
        '''What to do when leaving this mode'''
        pass

    def Init(self):
        '''What to do when entering this mode'''
        pass

class Ball:
    '''Simple ball class'''

    def __init__(self, filename, pos = (0.0, 0.0), speed = (0.0, 0.0)):
        '''Create a ball from image'''
        self.fname = filename
        self.surface = pygame.image.load(filename)
        self.rect = self.surface.get_rect()
        self.speed = speed
        self.pos = pos
        self.newpos = pos
        self.active = True

    def draw(self, surface):
        surface.blit(self.surface, self.rect)

    def action(self):
        '''Proceed some action'''
        if self.active:
            self.pos = self.pos[0]+self.speed[0], self.pos[1]+self.speed[1]
            self.speed = self.speed[0], self.speed[1] + GRAVITY

    def logic(self, surface):
        x,y = self.pos
        dx, dy = self.speed
        if x < self.rect.width/2:
            x = self.rect.width/2
            dx = -dx
        elif x > surface.get_width() - self.rect.width/2:
            x = surface.get_width() - self.rect.width/2
            dx = -dx
        if y < self.rect.height/2:
            y = self.rect.height/2
            dy = -dy
        elif y > surface.get_height() - self.rect.height/2:
            y = surface.get_height() - self.rect.height/2
            dy = -dy
        self.pos = x,y
        self.speed = dx,dy
        self.rect.center = intn(*self.pos)

class Universe:
    '''Game universe'''

    def __init__(self, msec, tickevent = pygame.USEREVENT):
        '''Run a universe with msec tick'''
        self.msec = msec
        self.tickevent = tickevent

    def Start(self):
        '''Start running'''
        pygame.time.set_timer(self.tickevent, self.msec)

    def Finish(self):
        '''Shut down an universe'''
        pygame.time.set_timer(self.tickevent, 0)

class GameWithObjects(GameMode):

    def __init__(self, objects=[]):
        GameMode.__init__(self)
        self.objects = objects
        self.bounced_objects = set()

    def locate(self, pos):
        return [obj for obj in self.objects if obj.rect.collidepoint(pos)]

    def collide(self, obj1, obj2):
        mask1 = pygame.mask.from_surface(obj1.surface)
        mask2 = pygame.mask.from_surface(obj2.surface)
        offset = int(obj1.pos[0] - obj2.pos[0]), int(obj1.pos[1] - obj2.pos[1])
        return mask1.overlap(mask2, offset)

    def bounce(self, obj1, obj2):
        obj1.speed, obj2.speed = obj2.speed, obj1.speed
        self.bounced_objects.add(frozenset((obj1, obj2)))

    def bounced(self, obj1, obj2):
        return frozenset((obj1, obj2)) in self.bounced_objects

    def Events(self, event):
        GameMode.Events(self, event)
        if event.type == Game.tickevent:
            for obj in self.objects:
                obj.action()
            for obj1 in self.objects:
                for obj2 in self.objects:
                    if obj1 == obj2:
                        continue
                    elif self.collide(obj1, obj2) and not self.bounced(obj1, obj2):
                        self.bounce(obj1, obj2) 
                    elif self.bounced(obj1, obj2):
                        self.bounced_objects.remove(frozenset((obj1, obj2)))

    def Logic(self, surface):
        GameMode.Logic(self, surface)
        for obj in self.objects:
            obj.logic(surface)

    def Draw(self, surface):
        GameMode.Draw(self, surface)
        for obj in self.objects:
            obj.draw(surface)

class GameWithDnD(GameWithObjects):

    def __init__(self, *argp, **argn):
        GameWithObjects.__init__(self, *argp, **argn)
        self.oldpos = 0,0
        self.drag = None

    def Events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            click = self.locate(event.pos)
            if click:
                self.drag = click[0]
                self.drag.active = False
                self.oldpos = event.pos
        elif event.type == pygame.MOUSEMOTION and event.buttons[0]:
                if self.drag:
                    self.drag.pos = event.pos
                    self.drag.speed = event.rel
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.drag:
                self.drag.active = True
                self.drag = None
        GameWithObjects.Events(self, event)

class RotatingBall(Ball):
    def __init__(self, *argp, **argn):
        Ball.__init__(self, *argp, **argn)
        self.angle = 0
        self.direction = random.choice([-1, 1])
        self.orig_surface = self.surface

    def logic(self, surface):
        self.angle += 1
        if self.angle > 360:
            self.angle = 1
        old_center = self.rect.center
        self.surface = pygame.transform.rotate(self.orig_surface, self.direction * self.angle)
        self.rect = self.surface.get_rect()
        self.rect.center = old_center
        Ball.logic(self, surface)




Init(SIZE)
Game = Universe(50)

Run = GameWithDnD()
for i in xrange(3):
    x, y = random.randrange(screenrect.w), random.randrange(screenrect.h)
    dx, dy = 1+random.random()*5, 1+random.random()*5
    Run.objects.append(RotatingBall("ball.gif",(x,y),(dx,dy)))

Game.Start()
Run.Init()
again = True
while again:
    event = pygame.event.wait()
    if event.type == pygame.QUIT:
        again = False
    Run.Events(event)
    Run.Logic(screen)
    Run.Draw(screen)
    pygame.display.flip()
Game.Finish()
pygame.quit()
