# -*- coding: utf-8 -*-
from numpy import random as random
import pygame
import numpy
import math
from particle import *
from sound import *

def nothing(a=None, b=None, c=None):
	pass

def shotBreakableWall(shot, tile):
	tile.life -= shot.damage
	if tile.life <= 0:
		tile.sprite = pygame.image.load(tile.spriteFile)
		walldown[numpy.random.randint(0,len(walldown))].play()
		tile.world.background.blit(tile.sprite, [tile.pos[0]*32,tile.pos[1]*32])
		tile.tankhit = nothing
		tile.shothit = nothing
		tile.colfunc = nothing
		tile.coldetect = False
		for i in xrange(10):
			tile.world.ps.create(Particle(tile.world, numpy.array(tile.pos)*32, numpy.random.randint(-4,5,2),random.randint(60,140)))

def shotBreakableObsidian(shot, tile):
	shotBreakableWall(shot,tile)

def quicksand(tank, tile):
	tank.multiplier = 2.0

def slowsand(tank, tile):
	tank.multiplier = 0.5

def mover(tank, tile, xdir, ydir):
	if tank.tilecol([xdir, ydir]):
		return
	tank.pos[0] += xdir
	tank.pos[1] += ydir

def rotateshot(shot, tile, direction):
	shot.rotateshot(direction)

def uptile(tank, tile):
	mover(tank, tile, 0, -1.0)

def downtile(tank, tile):
	mover(tank, tile, 0, 1.0)

def lefttile(tank, tile):
	mover(tank, tile, -1.0, 0)

def righttile(tank, tile):
	mover(tank, tile, 1.0, 0)

def rotup(shot, tile):
	rotateshot(shot, tile, math.pi/2.0)

def rotdown(shot, tile):
	rotateshot(shot, tile, 3.0*math.pi/2.0)

def rotleft(shot, tile):
	rotateshot(shot, tile, math.pi)

def rotright(shot, tile):
	rotateshot(shot, tile, 0)

tileTypeArguments = {
		"shotBreakableWall" : {
				"life"	: 50,
				"spriteFile" : "'gfx/destroyedstone.png'"
			},
		"shotBreakableObsidian" : {
				"life"	: 200,
				"spriteFile" : "'gfx/destroyedstone.png'"
			},
		"quicksand" : {
				
			},
		"slowsand" : {
			
			},
		
		"uptile" : {},
		"downtile" : {},
		"lefttile": {},
		"righttile": {},
		
		"rotup" : {},
		"rotdown" : {},
		"rotleft" : {},
		"rotright" : {},
	}

class Tile:
	def __init__(self, world, pos, filename, coldetect=False, tankhit=nothing,
			 shothit=nothing, colfunc=nothing, varArgs={}):
		self.sprite = pygame.image.load(filename)
		self.coldetect = coldetect
		self.tankhit = tankhit
		self.shothit = shothit
		self.colfunc = colfunc
		self.world = world
		self.pos = pos
		
		for k in varArgs:
			exec("self." + k + " = " + str(varArgs[k]))

	def blitTo(self, surface, pos):
		surface.blit(surface, self.sprite, pos)

class WeightingHandler:
	def __init__(self):
		self.weightings = []
		self.total = 0
	
	def addWeighting(self, val):
		self.weightings.append(val)
		self.total += val
	
	def getRandomIndex(self):
		rndVal = random.random()*self.total
		
		index = -1
		indexSum = 0
		while indexSum < rndVal:
			index+=1
			indexSum += self.weightings[index]
		
		return index

class World:
	def __init__(self, ps, shots):
		self.shots = shots
		self.ps = ps
	
	def load(self, fileStr, screen_width, screen_height):
		self.screen_width = screen_width
		self.screen_height = screen_height
		self.tiles = []
		fp = open(fileStr, "r")
		lines = fp.readlines()
		
		# Split level file into chunks
		lvLines = []
		infoLines = []
		typeState = 0
		for L in lines:
			L = L.strip("\n\r")
			if len(L)==0:
				continue
				
			if L == "---":
				typeState+=1
				continue
			if typeState == 0:
				lvLines.append(L)
			elif typeState == 1:
				infoLines.append(L)
		
		# Create tile types
		tileTypes = {}
		weightIndexes = WeightingHandler()
		for L in infoLines:
			line = [val for val in L.split("\t") if val != ""]
			for string in line:
				if len(string)==0:
					print("Empty")
			
			# TILE DATA
			tid = int(line[0])
			sprite = line[1]
			isCol = int(line[2])
			
			# Tile collision functions
			tankCol = eval(line[3])
			shotHit = eval(line[4])
			tileCol = eval(line[5])
			
			# Tile arguments
			tileArgList = {}
			if line[3] in tileTypeArguments:
				tileArgList.update(tileTypeArguments[line[3]])
			if line[4] in tileTypeArguments:
				tileArgList.update(tileTypeArguments[line[4]])
			if line[5] in tileTypeArguments:
				tileArgList.update(tileTypeArguments[line[5]])
			
			if len(line)>=7:
				weighting = float(line[6])
			else:
				weighting = 1.0
			weightIndexes.addWeighting(weighting)
			
			# END
			
			tileTypes[tid] = (sprite, isCol, tankCol, shotHit, tileCol, tileArgList)
		
		
		# Create tiles
		# Random:
		self.tiles = []
		p1y = screen_height/32-5
		p1x = screen_width/32-5
		if lvLines[0] == "random":
			for y in xrange(screen_height/32):
				tileLine = []
				for x in xrange(screen_width/32):
					if (x in [3,4,5] and y in [3,4,5]) or (x in [p1x, p1x+1, p1x+2] and y in [p1y, p1y+1, p1y+2]):
						T = tileTypes[0]
					else:
						T = tileTypes[weightIndexes.getRandomIndex()]
					tileLine.append( Tile( self, (x,y), T[0], T[1], T[2], T[3], T[4], T[5] ) )
				self.tiles.append(tileLine)
		# Normal:
		else:
			y=0
			for L in lvLines:
				tileLine = []
				
				Lspl = L.split(" ")
				x=0
				for n in Lspl:
					T = tileTypes[int(n)]
					tileLine.append( Tile( self, (x,y), T[0], T[1], T[2], T[3], T[4], T[5] ) )
					x+=1
				
				self.tiles.append(tileLine)
				y+=1
		
		fp.close()
		pass
	
	def getTile(self,pos):
		if pos[0] < 0 or pos[1] < 0 or pos[0] >= self.screen_width or pos[1] >= self.screen_height:
			return None
		else:
			return self.tiles[int(pos[1])/32][int(pos[0])/32]
	
	def process(self):
		pass
	
	def draw(self, surf):
		self.background = surf
		for y in xrange(len(self.tiles)):
			for x in xrange(len(self.tiles[y])):
				tile = self.tiles[y][x]
				surf.blit(tile.sprite, [x*32,y*32])
	def checkCollision(self, pos):
		if pos[0] < 0 or pos[1] < 0 or pos[0] > self.screen_width or pos[1] > self.screen_height:
			return True
		return self.tiles[int(pos[1])/32][int(pos[0])/32].coldetect
