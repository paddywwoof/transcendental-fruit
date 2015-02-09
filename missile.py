#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

import demo
import random
import pi3d

L_R = (0.0, 0.0, 0.0, 0.001, -0.001)
U_D = (0.0, 0.0, 0.0, 0.0, -0.0001)

########################################################################
class Missile(pi3d.Model):
  def __init__(self, m_type, bumpimg, reflimg, shader, clone=None):
    if clone == None:
      super(Missile, self).__init__(file_string='models/missile{}.obj'.format(m_type))
    else:
      super(Missile, self).__init__(file_string='__clone__')
      self.buf = clone.buf
      self.vGroup = clone.vGroup
    self.set_normal_shine(bumpimg, 1.0, reflimg, 0.2)
    print(shader)
    self.set_shader(shader)
    self.m_type = m_type
    self.flag = False
    self.l_r = L_R[m_type] # left/right curve factor
    self.u_d = U_D[m_type] # up/down curve factor

  def launch(self, loc, dirctn, speed, targets=None, g_asteroid=0.0, g_missile=0.0):
    self.loc = loc
    self.dx = dirctn[0] * speed
    self.dy = dirctn[1] * speed
    self.dz = dirctn[2] * speed
    self.targets = targets
    if targets:
      self.last_dist = [10000.0 for t in targets]
    self.g_asteroid = g_asteroid
    self.g_missile = g_missile

  def move(self):
    self.loc[0] += self.dx
    self.loc[1] += self.dy
    self.loc[2] += self.dz
    self.position(*self.loc)
    self.rotateIncZ(3.3)
    self.rotateIncY(1.02)
    self.dx -= self.dz * self.l_r
    self.dy += self.dz * self.u_d
    self.dz += self.dx * self.l_r - self.dy * self.u_d

  def test_hits(self):
    if self.targets:
      dist_list = []
      nearest_dist = 10000
      nearest_i = -1
      for i, t in enumerate(self.targets):
        if t.hit:
          dist_list.append(10000)
          #print(i)
        else:
          dx, dy, dz = t.loc[0] - self.loc[0], t.loc[1] - self.loc[1], t.loc[2] - self.loc[2]
          dist = (dx ** 2 + dy ** 2 + dz ** 2) ** 0.5
          dist_list.append(dist)
          #print(dist, i, t.threshold, nearest_dist, len(self.targets))
          if dist < t.threshold and dist < nearest_dist:
            nearest_dist = dist
            nearest_i = i
          if dist < 100.0 and self.g_asteroid != 0.0:
            g_factor = self.g_asteroid / dist ** 3
            t.dx -= dx * g_factor
            t.dy -= dy * g_factor
            t.dz -= dz * g_factor
          if dist < 100.0 and self.g_missile != 0.0:
            g_factor = self.g_missile / dist ** 3
            self.dx += dx * g_factor
            self.dy += dy * g_factor
            self.dz += dz * g_factor
          
      if nearest_i > -1 and dist_list[nearest_i] > self.last_dist[nearest_i]:
        return nearest_i, self.last_dist[nearest_i]
      self.last_dist[:] = dist_list[:]
    return -1, 10000
