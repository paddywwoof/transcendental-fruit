#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

import demo
import random
import pi3d

########################################################################
class Missile(pi3d.Model):
  def __init__(self, m_type, bumpimg, reflimg, shader):
    super(Missile, self).__init__(file_string='models/missile{}.obj'.format(m_type))
    self.set_normal_shine(bumpimg, 1.0, reflimg, 0.2)
    self.set_shader(shader)

  def launch(self, loc, mtrx, speed, targets=None):
    self.loc = loc
    self.dx = mtrx[0, 3] * speed
    self.dy = mtrx[1, 3] * speed
    self.dz = mtrx[2, 3] * speed
    self.targets = targets
    if targets:
      self.last_dist = [10000.0 for t in targets]

  def move(self):
    self.loc[0] += self.dx
    self.loc[1] += self.dy
    self.loc[2] += self.dz
    self.position(*self.loc)
    self.rotateIncZ(3.3)

  def test_hits(self):
    if self.targets:
      dist_list = []
      nearest_dist = 10000
      nearest_i = -1
      for i, t in enumerate(self.targets):
        dx, dy, dz = t.loc[0] - self.loc[0], t.loc[1] - self.loc[1], t.loc[2] - self.loc[2]
        dist = (dx ** 2 + dy ** 2 + dz ** 2) ** 0.5
        dist_list.append(dist)
        if dist < nearest_dist and not t.hit:
          nearest_dist = dist
          nearest_i = i
      if nearest_i > -1 and dist_list[nearest_i] > self.last_dist[nearest_i]:
        return nearest_i, self.last_dist[nearest_i]
      self.last_dist[:] = dist_list[:]
    return -1, 10000
