# -*- coding: utf-8 -*-
class BoundingBox:
	def __init__(self, topLeft, botRight)
		self.tl = topLeft
		self.br = botRight

def check_collision(p1, B1, p2, B2):
	ret = [False, None]
	
	offx = p2[0]-p1[0]
	offy = p2[1]-p1[1]
	
	left = B1.br[0] - (B2.tl[0]+offx)
	if(left <= 0):
		return ret
	
	right = (B2.br[0]+offx) - B1.tl[0]
	if(right <= 0):
		return ret
	
	top = B1.br[1] - (B2.tl[1]+offy)
	if(top <= 0):
		return ret
	
	bot = (B2.br[1]+offy) - B1.tl[1]
	if(bot <= 0):
		return ret
	
	xmin = left if left < right else right
	ymin = top if top < bot else bot
	
	ret[0] = True
	if(xmin < ymin):
		ret[1] = (left if left<right else -right, 0.0)
	else:
		ret[1] = (0.0, top if top<bot else -bot)
	
	return ret
