#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

class Level(object):
  def __init__(self,
                minv,           # min score for this level
                maxv,           # max score for this level
                num,            # nuber of asteroids
                start_loc,      # centre of start location rel to camera
                start_range,    # range of start location
                speed,          # speed of asteroids
                speed_range,    # range of speeds
                missile,        # missile type to use
                go_speed,       # camera speed
                start_location, # start location of camera
                num_good,       # number of 'good' asteroids (not to hit)
                num_missiles):  # number simultaneous missiles
    self.minv = minv
    self.maxv = maxv
    self.num = num
    self.start_loc = start_loc
    self.start_range = start_range
    self.speed = speed
    self.speed_range = speed_range
    self.missile = missile
    self.go_speed = go_speed
    self.start_location = start_location
    self.num_good = num_good
    self.num_missiles = num_missiles

levels = [Level(0.0, 0.2, 2, (0.0,0.0,100.0), (100.0,200.0,100.0), 0.02, 0.01, 0, 0.05, (0.0,0.0,0.0), 0, 1),
          Level(0.2, 0.5, 5, (0.0,0.0,500.0), (400.0,100.0,300.0), 0.2,  0.2,  0, 0.1, (700.0,0.0,500.0), 0, 2),
          Level(0.5, 1.0, 7, (0.0,0.0,400.0), (400.0,300.0,200.0), 0.4,  0.3,  0, 0.3, (1000.0,0.0,300.0), 0, 3)]
