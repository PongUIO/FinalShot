import numpy
import pygame
from sound import *
from particle import *
e = 0.1

class Tank:
	def __init__(self, pos, sprite, life, world):
		self.world = world
		self.life = life
		self.startlife = life
		self.pos = numpy.array(pos)
		self.sprite = sprite
		self.direction = {1:0, 2:0, 3:0, 4:0}
		self.rotate = {1:360, 2:90, 3:180, 4:270}
		self.hpcolor = (100,100,100)
		self.shotdirection = 1

	def draw(self, screen):
		if self.life <= 0:
			return False
		angle = 0.
		dirs = 0
		for i in self.direction.keys():
			if self.direction[i] != 0:
				angle += self.rotate[i]
				dirs += 1
		if dirs == 0:
			dirs = 1
		if self.direction[1] == 1 and self.direction[2] == 1:
			angle = 90
		if angle == 0:
			angle = self.rotate[self.shotdirection]
		if angle/dirs%90 == 45:
			displace = numpy.array([-10,-10])
		else:
			displace = numpy.array([0,0])
		screen.blit(pygame.transform.rotate(self.sprite, angle/dirs), self.pos+displace)
		return True

	def collides(self, other):
		if self.life <= 0:
			return
		for pos in [other.pos, 
			other.pos+[other.size[0],0], 
			other.pos+[other.size[0],other.size[1]], 
			other.pos+[0,other.size[1]]]:
			if pos[0] < self.pos[0]+48 and pos[0] > self.pos[0] and pos[1] < self.pos[1] + 48 and pos[1] > self.pos[1]:
				return True
		return False

	def __call__(self):
		pass
	
class PlayerTank(Tank):
	healaura = pygame.image.load("gfx/healaura.png")
	def __init__(self, sprite, pos, playernumber, types, loadtimes, icons, life, world, regenrate, startregen):
		Tank.__init__(self, pos, sprite, life, world)
		self.startpos = pos
		self.loadtimes = loadtimes
		self.reloadstate = 0
		self.curweapon = 0
		self.lastshot = 0
		self.showaura = False
		self.regenrate = regenrate
		self.startregen = startregen
		self.regen = startregen
		self.types = types
		self.firing = False
		self.icons = []
		self.multiplier = 1.0
		for i in icons:
			self.icons.append(pygame.image.load(i))
		self.wepdisplay = 100
		self.movement = {1:numpy.array([0,-1]), 4:numpy.array([1,0]), 3:numpy.array([0,1]), 2:numpy.array([-1,0])}
		if (playernumber == 0):
			self.keys = {pygame.K_UP:1, pygame.K_DOWN:3, pygame.K_RIGHT:4, pygame.K_LEFT:2}
			self.swap = pygame.K_RSHIFT
			self.shoot = pygame.K_RCTRL
			self.hpcolor = (225,0,0)
		else:
			self.keys = {pygame.K_w:1, pygame.K_s:3, pygame.K_d:4, pygame.K_a:2}
			self.shoot = pygame.K_r
			self.swap = pygame.K_t
			self.hpcolor = (0,0,225)
		self.playernumber = playernumber

	def draw(self, screen):
		if (Tank.draw(self, screen)):
			if (self.wepdisplay > 0):
				screen.blit(self.icons[self.curweapon], self.pos + numpy.array([8, -50]))
			pygame.draw.rect(screen, self.hpcolor, [self.pos+numpy.array([0,-7]), 
				numpy.array([int(48*(self.life/float(self.startlife))), 7])]) #HP
			pygame.draw.rect(screen, (255,255,0), [self.pos+numpy.array([0,-15]), 
				numpy.array([int(48*((self.loadtimes[self.lastshot]-self.reloadstate)/float(self.loadtimes[self.lastshot]))), 7])]) #Reload
			pygame.draw.rect(screen, (0,0,0), [self.pos+numpy.array([0,-7]), numpy.array([48, 7])], 1)
			pygame.draw.rect(screen, (0,0,0), [self.pos+numpy.array([0,-15]), numpy.array([48, 7])], 1)
			if self.showaura:
				screen.blit(self.healaura, self.pos-numpy.array([8,8]))


	def handlekey(self, event):
		if self.life <= 0:
			return
		if self.keys.has_key(event.key):
			self.direction[self.keys[event.key]] = 1
			self.shotdirection = self.keys[event.key]
		elif self.shoot == event.key:
			if self.reloadstate > 0:
				self.firing = False
			else:
				self.firing = not self.firing
		elif self.swap == event.key:
			self.curweapon += 1
			if (self.curweapon == len(self.types)):
				self.curweapon = 0
			self.wepdisplay = 100
			self.firing = False

	def endmove(self, event):
		if self.keys.has_key(event.key):
			self.direction[self.keys[event.key]] = 0
			self.shotdirection = self.keys[event.key]
	def tilecol(self, direction):
		for i in [0, 24, 47]:
			for j in [0, 24, 47]:
				tile = self.world.getTile(self.pos+numpy.array([i,j]) + direction)
				if tile == None:
					return True
				if tile.coldetect:
					tile.tankhit(self, tile)
					return True
		return False

	def __call__(self):
		if self.life <= 0:
			return
		if self.wepdisplay > 0:
			self.wepdisplay -= 1
		if self.reloadstate > 0:
			self.reloadstate -= 1
			if self.reloadstate < 0:
				self.reloadstate = 0
		if self.life < self.startlife:
			if self.regen > 0:
				self.regen -= 1
			if self.regen <= 0:
				self.life += 1
				self.showaura = True
				self.regen = self.regenrate+self.regen
				for p in numpy.random.randint(-8,48,(5,2)):
					self.world.ps.create(Plus(self.world, self.pos+p, [0,0], numpy.random.randint(20,40)))
				if (self.life == self.startlife):
					self.showaura = False
		if self.firing == True:
			if self.reloadstate == 0:
				if self.reloadstate > 0:
					self.reloadstate = 0
					return
				direction = numpy.array([0,0])
				for key in self.direction.keys():
					if self.direction[key] != 0:
						direction += self.movement[key]
				if direction[0] == 0 and direction[1] == 0:
					direction = self.movement[self.shotdirection]
				sumdir = 0.0
				for i in direction:
					sumdir += i**2
				sumdir = numpy.sqrt(sumdir)
				self.world.shots.create(self.types[self.curweapon](self.pos+numpy.array([19,19]), (direction/sumdir), self))
				self.lastshot = self.curweapon
				self.reloadstate = self.loadtimes[self.curweapon]
				if (self.curweapon == 0):
					mgun[numpy.random.randint(0,len(mgun))].play()
				elif (self.curweapon == 4):
					laser[numpy.random.randint(0,len(laser))].play()
				if self.reloadstate >= 20:
					self.firing = False
		direction = numpy.array([0.,0.])
		self.multiplier = 1.0
		tile = self.world.getTile(self.pos+numpy.array([24,24]))
		tile.tankhit(self, tile)
		if self.multiplier < 0.5:
			self.multiplier = 0.5
		for i in range(int((2*self.multiplier)+0.1)):
			for key in self.direction.keys():
				if self.direction[key] != 0:
					if not self.tilecol(self.movement[key]):
						self.pos += self.movement[key]



	def reset(self):
		self.firing = False
		self.pos = self.startpos
		self.life = self.startlife
		self.reloadstate = 0
		self.curweapon = 0
		self.wepdisplay = 100
		self.showaura = False
