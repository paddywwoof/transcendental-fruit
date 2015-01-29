#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

class Level(object):
  def __init__(self, minv, maxv, num, start_loc, start_range, speed, speed_range, missile, go_speed):
    self.minv = minv
    self.maxv = maxv
    self.num = num
    self.start_loc = start_loc
    self.start_range = start_range
    self.speed = speed
    self.speed_range = speed_range
    self.missile = missile
    self.go_speed = go_speed

levels = [Level(0.0, 0.2, 2, (0.0,   0.0, 100.0), (100.0, 200.0, 100.0), 0.02, 0.01, 0, 0.05),
          Level(0.2, 0.5, 5, (0.0,   0.0, 500.0), (400.0, 100.0, 300.0), 0.2,  0.2,  0, 0.1),
          Level(0.5, 1.0, 7, (0.0,   0.0, 400.0), (400.0, 300.0, 200.0), 0.4,  0.3,  0, 0.3)]
