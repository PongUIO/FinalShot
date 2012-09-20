# -*- coding: utf-8 -*-
import pygame
pygame.mixer.pre_init(44100,-16, 2, 512)
pygame.init()
import os
import sys
import time
import numpy
random = numpy.random
from tank import *
from tile import *
from particle import *
from menu import *

screen_width = 1280
screen_height = 800


class Shot:
	def __init__(self, pos, direction, speed, player):
		self.pos = numpy.array(pos)
		self.vel = numpy.array(direction*speed)
		self.pid = player.playernumber
		self.colPos = numpy.array([0,0])
		self.damage = 0
		self.rotate = False
		self.direction = None
	
	def __call__(self):
		return False # Kill dummy shots instantaneously
	
	def draw(self, screen):
		pass
	
	# Will return the tile we're colliding with
	def checkTileCollision(self):
		pass
	def playerHitTrigger(self, i):
		pass
	def rotateshot(self, direction):
		if self.rotate:
			speed = 0.1*max(numpy.sqrt(sum(self.vel**2)), 5)
			mod = [speed*numpy.cos(direction), -speed*numpy.sin(direction)]
			self.vel += mod
			if (self.direction != None):
				self.direction += mod

			#self.vel += [self.step*0.3*speed*numpy.cos(temp), self.step*0.3*speed*numpy.sin(temp)]
			#print self.vel

class StraightShot(Shot):
	sprite = pygame.image.load("gfx/bullet.png")
	def __init__(self, pos, direction, player):
		self.size = self.sprite.get_size()
		Shot.__init__(self, pos, direction, 8, player)
		self.damage = 6
		self.colPos = numpy.array(self.sprite.get_rect()[2:4])/2
	
	def __call__(self):
		self.pos[0] += self.vel[0]
		self.pos[1] += self.vel[1]
		temp = self.pos + self.colPos
		if temp[0] < 0 or temp[1] < 0 or temp[0] >= screen_width or temp[1] >= screen_height:
			return True
		tile = world.getTile(temp)
		if (tile and tile.coldetect):
			tile.shothit(self, tile)
			self.playerHitTrigger(35)
			return True
		elif (tile):
			tile.shothit(self, tile)
		elif (tile == None):
			return True

		return False
	
	def draw(self, screen):
		screen.blit(self.sprite, self.pos)

class RocketShot(StraightShot):
	spritenr = pygame.image.load("gfx/rocket.png")
	def __init__(self, pos, direction, player):
		Shot.__init__(self, pos, direction, 6., player)
		self.rotate = True
		self.world = player.world
		self.damage = 50
		self.player = player
		self.direction = direction
		temp = direction/numpy.sqrt(sum(direction**2))
		angle = numpy.arctan2(temp[0], temp[1])-numpy.pi
		if angle < 0:
			angle += numpy.pi*2
		self.sprite = pygame.transform.rotate(self.spritenr, (angle/numpy.pi)*180)
		self.size = self.sprite.get_size()
		self.colPos = numpy.array(self.sprite.get_rect()[2:4])/2
	def draw(self, screen):
		for i in range(3):
			self.player.world.ps.create(Smoke(self.world, self.pos, -0.5*self.vel+random.randint(-4,5,2), 30))
		screen.blit(self.sprite, self.pos)
	def __call__(self):
		self.vel *= 1.03
		while (numpy.sqrt(sum(self.vel**2)) < 1):
			self.vel *= 1.01
		return StraightShot.__call__(self)

class NapalmRocketShot(RocketShot):
	spritenr = pygame.image.load("gfx/rocketnapalm.png")
	def __init__(self, pos, direction, player):
		Shot.__init__(self, pos, direction, 3, player)
		self.rotate = True
		self.player = player
		self.world = player.world
		self.damage = 15
		self.player = player
		self.direction = direction
		self.life = 90
		temp = direction/numpy.sqrt(sum(direction**2))
		angle = numpy.arctan2(temp[0], temp[1])-numpy.pi
		if angle < 0:
			angle += numpy.pi*2
		self.sprite = pygame.transform.rotate(self.spritenr, (angle/numpy.pi)*180)
		self.size = self.sprite.get_size()
		self.colPos = numpy.array(self.sprite.get_rect()[2:4])/2
	def __call__(self):
		self.life -= 1
		if self.life < 0:
			self.playerHitTrigger(35)
			return True
		else:
			return RocketShot.__call__(self)
	def playerHitTrigger(self, i):
		for i in range(i):
			self.world.shots.create(Napalm(self.pos-self.vel*2, (random.random(2)-0.5)*4, self.player))

class Napalm(StraightShot):
	sprite = pygame.image.load("gfx/napalm.png")
	def __init__(self, pos, direction, player):
		Shot.__init__(self, pos, direction, 1, player)
		self.rotate = True
		self.size = self.sprite.get_size()
		self.direction = direction
		self.world = player.world
		self.damage = 8
		self.life = random.randint(200,500)
		self.pid = 2 #FRIENDLY FIRE!
		self.colPos = numpy.array(self.sprite.get_rect()[2:4])/2
	def __call__(self):
		self.vel = numpy.array(self.direction*(self.life*4/750.))
		self.life -= 1
		if self.life < 0:
			return True
		return StraightShot.__call__(self)

class FlamethrowerShot(Napalm):
	def __init__(self, pos, direction, player):
		Napalm.__init__(self, pos, direction*5, player)
		self.rotate = True
		self.pid = player.playernumber
		self.life = random.randint(300,400)
		self.damage = 1
		self.colPos = numpy.array(self.sprite.get_rect()[2:4])/2

class Flamethrower(Shot):
	def __init__(self, pos, direction, player):
		self.player = player
		self.pos = player.pos
		self.direction = direction
	def __call__(self):
		for i in (numpy.random.random(4)-0.5)*0.1*numpy.pi:
			angle = numpy.arctan2(self.direction[1], self.direction[0]) + i
			temp = numpy.array([numpy.cos(angle), numpy.sin(angle)])
			self.player.world.shots.create(FlamethrowerShot(self.pos+numpy.array([12,12]), temp*0.6, self.player))
		return True

class SniperShot(StraightShot):
	sprite = pygame.image.load("gfx/snipershot.png")
	def __init__(self, pos, direction, player):
		StraightShot.__init__(self, pos, direction, player)
		self.rotate = True
		self.damage = 70
		self.vel *= 2
		self.player = player
		self.startpos = pos
		self.colPos = numpy.array(self.sprite.get_rect()[2:4])/2
	def draw(self, screen):
		StraightShot.draw(self, screen)
		length = int(sum(numpy.sqrt(self.vel**2))) + 1
		for i in range(length):
			self.player.world.ps.create(Dot(self.player.world, self.pos-(self.vel/length)*(length/2-i), numpy.array([0,0]), length-i))
	def __call__(self):
		while (numpy.sqrt(sum(self.vel**2)) < 1):
			self.vel *= 1.01
		return StraightShot.__call__(self)
		

class ShotSystem:
	def __init__(self, ps):
		self.tanks = []
		self.ps = ps
		self.shotPack = []
	
	def __call__(self):
		eraseList = []
		for shot in self.shotPack:
			if shot():
				eraseList.append(shot)
				hit[numpy.random.randint(0,len(hit))].play()
		self.removeShots(eraseList)
		eraseList = []
		for shot in self.shotPack:
			for tank in self.tanks:
				if shot.pid != tank.playernumber and tank.collides(shot):
					tank.life -= shot.damage
					tank.regen = tank.startregen
					tank.showaura = False
					shot.playerHitTrigger(5)
					eraseList.append(shot)
					hit[numpy.random.randint(0,len(hit))].play()
					break
		self.removeShots(eraseList)
	def clean(self):
		self.shotPack = []
	def create(self, shot):
		self.shotPack.append(shot)
	
	def removeShots(self, eraseList):
		for er in eraseList:
			self.shotPack.remove(er)
	
	def draw(self, screen):
		for shot in self.shotPack:
			shot.draw(screen)
	def add(self, tank):
		self.tanks.append(tank)


ps = ParticleSystem()
tank = pygame.image.load("gfx/tank.png")
tank2 = pygame.image.load("gfx/tank2.png")
shots = ShotSystem(ps)
world = World(ps, shots)
weps = [StraightShot, RocketShot, NapalmRocketShot, Flamethrower, SniperShot]
icons = ["gfx/cannonicon.png", "gfx/rocketicon.png", "gfx/rocketnapalmicon.png", "gfx/napalmicon.png", "gfx/snipershoticon.png"]
loadtimes = [10, 60, 120, 6, 150]
regen = 10
startregen = 180
startlife = 100
ptank1 = PlayerTank(tank, [screen_width-148., screen_height-148.], 0, weps, loadtimes, icons, startlife, world, regen, startregen)
ptank2 = PlayerTank(tank2, [100., 100.], 1, weps, loadtimes,icons, startlife, world, regen, startregen)
shots.add(ptank1)
shots.add(ptank2)
font = pygame.font.SysFont("Bitstream Vera Sans Mono", 24)
fgcolor = (0,0,0)
kd = ["Kills: ", "Deaths:"]

def play(screen, level, report):
	gspeed = 60
	stats = [[0,0],[0,0]]
	world.load(level, screen_width, screen_height)
	background = surface_init()
	ctime = time.time()
	repLTime = ptime = ctime
	labels = []
	showscores = False
	ratio = 0.5
	stime = 0.0
	if ptank2.life <= 0:
		stats[0][0] += 1
		stats[1][1] += 1
	if ptank1.life <= 0:
		stats[0][1] += 1
		stats[1][0] += 1
	ptank1.reset()
	ptank2.reset()
	background = surface_init()
	shots.clean()
	ps.clean()
	if report:
		print "start 100"
	while True:
		event = pygame.event.wait()
		ctime = time.time()
		dtime = ctime - ptime
		if report and (ctime - repLTime) > 1:
			repLTime = ctime
			print "time_request 1"
		for i in xrange(int(dtime*gspeed)):
			ptank1()
			ptank2()
			shots()
			ps()
		ptime = (ptime)+(1./gspeed)*int(dtime*gspeed)
		if event.type == pygame.VIDEOEXPOSE:
			screen.blit(background, [0,0])
			ptank1.draw(screen)
			ptank2.draw(screen)
			ps.draw(screen)
			shots.draw(screen)
			if showscores:
				pygame.draw.rect(screen,(int(50+205*ratio), 0, int(50+205*(1-ratio))),[100,100,screen_width-200, screen_height-200], 0)
				for i in xrange(2):
					for j in xrange(3):
						screen.blit(labels[i][j], (100+i*((screen_width-200)/2), 100+j*24))
			pygame.display.flip()
			pygame.event.clear(pygame.VIDEOEXPOSE)

		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				print "exit 0" #+ str(stats[1][1]) + ", " + str(stats[0][1])
				return 0
			elif event.key == pygame.K_o:
				if ptank2.life <= 0:
					stats[0][0] += 1
					stats[1][1] += 1
				if ptank1.life <= 0:
					stats[0][1] += 1
					stats[1][0] += 1
				ptank1.reset()
				ptank2.reset()
				world.load(level, screen_width, screen_height)
				background = surface_init()
				shots.clean()
				ps.clean()
			elif event.key == pygame.K_l:
				showscores = True
				if stats[0][0] == 0 and stats[1][0] == 0:
					ratio = 0.5
				else:
					ratio = stats[0][0]/float((stats[0][0]+stats[1][0]))
				labels = []
				for i in xrange(2):
					tlabels = []
					tlabels.append(font.render("Player %9i" %(i+1), 1, fgcolor))
					for j in xrange(2):
						tlabels.append(font.render("%s%9i" %(kd[j], stats[i][j]), 1, fgcolor))
					labels.append(tlabels)
			elif event.key == pygame.K_k:
				if gspeed >= 60:
					gspeed = 10
				else:
					gspeed += 10
			else:
				ptank1.handlekey(event)
				ptank2.handlekey(event)
				
		elif event.type == pygame.KEYUP:
			if event.key == pygame.K_l:
				showscores = False
			ptank1.endmove(event)
			ptank2.endmove(event)


def surface_init():
	mysurf = pygame.Surface((screen_width, screen_height))
	world.draw(mysurf)
	return mysurf

def main(mode, report, fullscreen):
	if report:
		print "initializing"
	if mode == 2:
		level = "levels/level"
	framerate = 60
	pygame.time.set_timer(pygame.VIDEOEXPOSE, 1000 / framerate)
	screen = pygame.display.set_mode((screen_width, screen_height))
	if fullscreen:
		pygame.display.toggle_fullscreen()
	while mode != -1:
		if mode == 0:
			mode, level = menu(screen)
		elif mode == 1:
			mode = play(screen, level, report)
		elif mode == 2:
			play(screen, level, report)
			return


if __name__ == "__main__":
	mode = 0
	report = False
	fullscreen = False
	for arg in sys.argv:
		if (arg == "play"):
			mode = 2
		elif (arg == "report"):
			report = True
		elif (arg == "fullscreen"):
			fullscreen = True
	main(mode, report, fullscreen)
