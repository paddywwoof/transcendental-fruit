#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

import demo
import random
import pi3d

L_R = (0.0, 0.0, 0.0, 0.001, -0.001)
U_D = (0.0, 0.0, 0.0, 0.0, -0.0001)

########################################################################
class Dust(pi3d.Points):
  def __init__(self, shader, spread):
    num = 1
    for i in spread:
      num *= i
    num = int(num / 60)
    verts = [] # list of xyz tuples
    self.xyz = set() # set of xyz tuples for quick checking membership
    for i in range(num):
      loc = tuple(int(random.gauss(0, spread[j])) for j in range(3))
      verts.append(loc)
      self.xyz.add((int(loc[0]/5), int(loc[1]/5), int(loc[2]/5)))
      
    super(Dust, self).__init__(vertices=verts, material=(0.6, 0.6, 1.0), point_size=400)
    self.set_shader(shader)
    self.set_fog((1.0, 0.0, 0.0, 0.0), 500.0)

  def launch(self, box_location, box_size, target, speed, speed_range):
    # make start relative to self
    self.loc = [box_location[i] + target[i] + (random.random() - 0.5) * box_size[i] for i in range(3)]
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

  def test_hit(self, target):
    xyz = tuple(int((target[i] + 0.5 - self.loc[i])/5) for i in range(3))
    if xyz in self.xyz:
      return True
    return False

