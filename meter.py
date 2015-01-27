#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

import demo
import pi3d

########################################################################
class Meter(pi3d.Sprite):
  def __init__(self, shader, camera, x_pos, width, height, value=0.5,
              material=[[0.9, 0.1, 0.1], [0.1, 0.9, 0.4]]):
    super(Meter, self).__init__(camera=camera, w=width, h=height, x=x_pos, z=1.0)
    self.height = height
    self.material = material
    self.change_reading(value)
    self.set_shader(shader)
    self.set_alpha(0.15)

  def change_reading(self, value):
    mix = [self.material[0][i] * (1.0 - value) + self.material[1][i] * value for i in range(3)]
    self.set_material(mix)
    self.positionY(self.height * (value - 1.0))
