#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

import demo
import random
import pi3d

########################################################################
class Asteroid(pi3d.Model):
  def __init__(self, bumpimg, reflimg, explimg, threshold=15.0):
    super(Asteroid, self).__init__(file_string='models/asteroid.obj')
    self.bumpimg = bumpimg
    self.reflimg = reflimg
    self.explimg = explimg
    self.explode_seq = -1
    self.threshold = threshold
    self.hit = False
    
  def launch(self, shader, texture, box_location, box_size, target, speed, speed_range):
    self.shader = shader
    self.set_draw_details(shader, [texture, self.bumpimg, self.reflimg], 1.0, 0.2)
    self.loc = box_location
    for i in range(3):
      self.loc[i] += (random.random() - 0.5) * box_size[i]
    self.position(*self.loc)
    dx, dy, dz = target[0] - self.loc[0], target[1] - self.loc[1], target[2] - self.loc[2]
    dist = (dx ** 2 + dy ** 2 + dz ** 2) ** 0.5
    speed += (random.random() - 0.5) * speed_range
    self.dx = speed * dx / dist * (0.6 + random.random() * 0.8)
    self.dy = speed * dy / dist * (0.6 + random.random() * 0.8)
    self.dz = speed * dz / dist * (0.6 + random.random() * 0.8)
    
  def move(self):
    self.loc[0] += self.dx
    self.loc[1] += self.dy
    self.loc[2] += self.dz
    self.position(*self.loc)
    self.rotateIncY(0.51)
    self.rotateIncZ(0.21)

  def test_hit(self, dist):
    print(dist, self.threshold)
    if dist < self.threshold:
      self.set_draw_details(self.shader, [self.explimg, self.bumpimg, self.reflimg], 1.0, 0.5)
      self.explode_seq = 0
      self.hit = True
      return True
    return False

  def draw(self):
    if self.explode_seq > 200:
      return
    elif self.explode_seq > -1:
      sc_fact = 1.015 ** self.explode_seq
      self.scale(sc_fact, sc_fact, sc_fact)
      self.set_alpha((200.0 - self.explode_seq) / 200.0)
      self.explode_seq += 1
    super(Asteroid, self).draw()
