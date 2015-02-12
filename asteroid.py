#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

import demo
import random
import pi3d

EXPLODE_N = 50

########################################################################
class Asteroid(pi3d.Model):
  def __init__(self, bumpimg, reflimg, explimg, threshold=10.0, clone=None):
    if clone == None:
      super(Asteroid, self).__init__(file_string='models/asteroid.obj')
    else:
      super(Asteroid, self).__init__(file_string='__clone__')
      self.buf = clone.buf
      self.vGroup = clone.vGroup
      self.shader = clone.shader
      self.textures = clone.textures
    self.bumpimg = bumpimg
    self.reflimg = reflimg
    self.explimg = explimg
    self.explode_seq = -1
    self.threshold = threshold
    self.hit = False
    self.correct_answer = False # mark an asteroid as the correct answer
    self.good = False # mark an asteroid as 'good' to loose marks if hit
    
  def launch(self, shader, texture, box_location, box_size, target, speed,
              speed_range, threshold=None, correct_answer=False, good=False):
    self.shader = shader
    self.texture = texture
    self.set_draw_details(shader, [self.texture, self.bumpimg, self.reflimg], 1.0, 0.2)
    # make start relative to self
    self.loc = [box_location[i] + target[i] + (random.random() - 0.5) * box_size[i] for i in range(3)]
    self.position(*self.loc)
    dx, dy, dz = target[0] - self.loc[0], target[1] - self.loc[1], target[2] - self.loc[2]
    dist = (dx ** 2 + dy ** 2 + dz ** 2) ** 0.5
    speed += (random.random() - 0.5) * speed_range
    self.dx = speed * dx / dist * (0.6 + random.random() * 0.8)
    self.dy = speed * dy / dist * (0.6 + random.random() * 0.8)
    self.dz = speed * dz / dist * (0.6 + random.random() * 0.8)
    if threshold:
      self.threshold = threshold
    self.correct_answer = correct_answer
    self.good = good
    self.hit = False
    self.explode_seq = -1
    self.scale(1.0, 1.0, 1.0)
    self.set_alpha(1.0)
    
  def move(self):
    self.loc[0] += self.dx
    self.loc[1] += self.dy
    self.loc[2] += self.dz
    self.position(*self.loc)
    self.rotateIncY(1.51)
    self.rotateIncZ(0.21)

  def test_hit(self, dist):
    if dist < self.threshold:
      self.explode_seq = 0
      self.hit = True
      return True
    return False

  def draw(self):
    if self.explode_seq > EXPLODE_N:
      return
    elif self.explode_seq > -1:
      sc_fact = 1.04 ** self.explode_seq
      self.scale(sc_fact, sc_fact, sc_fact)
      self.set_alpha((EXPLODE_N - self.explode_seq) / EXPLODE_N)
      self.explode_seq += 1
      super(Asteroid, self).draw(self.shader, [self.explimg, self.bumpimg,
                                  self.reflimg], 1.0, 0.5) #exploding
    else:
      super(Asteroid, self).draw(self.shader, [self.texture, self.bumpimg,
                                  self.reflimg], 1.0, 0.5) #not exploding
