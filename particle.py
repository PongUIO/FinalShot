# -*- coding: utf-8 -*-
import pygame
import numpy

class Particle:
	sprite=pygame.image.load("gfx/particle.png")
	def __init__(self, world, pos, vel, timeout):
		self.world = world
		self.pos = numpy.array(pos)
		self.vel = numpy.array(vel)
		self.timeout = timeout
	
	def __call__(self):
		self.pos += self.vel
		
		self.timeout -= 1
		if self.timeout <= 0:
			self.world.background.blit(self.sprite, self.pos)
			return True
		return False
	
	def draw(self, screen):
		screen.blit(self.sprite, self.pos)

		
class Smoke:
	sprite = pygame.image.load("gfx/smoke.png")
	def __init__(self, world, pos, vel, timeout):
		self.pos = numpy.array(pos)
		self.vel = numpy.array(vel)
		self.timeout = timeout
	
	def __call__(self):
		self.pos += self.vel
		self.timeout -= 1
		if self.timeout <= 0:
			return True
		return False
	
	def draw(self, screen):
		screen.blit(self.sprite, self.pos)

class Plus(Smoke):
	sprite = pygame.image.load("gfx/plus.png")

class Dot(Smoke):
	sprite = pygame.image.load("gfx/snipetrace.png")

class ParticleSystem:
	def __init__(self):
		self.particles = []
	
	def create(self, part):
		self.particles.append(part)
	
	def __call__(self):
		eraseList = []
		for p in self.particles:
			if p():
				eraseList.append(p)
		
		for p in eraseList:
			self.particles.remove(p)
	
	def draw(self, screen):
		for p in self.particles:
			p.draw(screen)
	def clean(self):
		self.particles = []
