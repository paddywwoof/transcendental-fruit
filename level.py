#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

class Level(object):
  def __init__(self,
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
                num_missiles,   # number simultaneous missiles
                missile_speed,  # missile launch speed
                threshold,      # proximity for destruction
                g_asteroid,     # inverse square attraction effect asteroid
                g_missile,      # inv square attract missile
                dust):          # tuple of dust spread
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
    self.missile_speed = missile_speed
    self.threshold = threshold
    self.g_asteroid = g_asteroid
    self.g_missile = g_missile
    self.dust = dust

#### base levels on q_pointer rather than score:-> 48 levels
levels = [##         num   start_loc        start_range      astd_sp rng  miss#  sp     start_locn   n_good n_miss miss_sp thsh g_a  g_m
          Level(0.02, 2, (0.0,0.0,100.0),  (100.0,200.0,100.0), 0.05, 0.01, 0, 0.05, (-1500.0,0.0,0.0),  0,   1,   1.0,    3.0, 0.0, 0.0, None),
          Level(0.04, 3, (0.0,0.0,100.0),  (100.0,200.0,100.0), 0.06, 0.01, 0, 0.06, (-1500.0,0.0,0.0),  0,   1,   1.0,    3.0, 0.0, 0.0, None),
          Level(0.06, 4, (0.0,0.0,100.0),  (100.0,200.0,100.0), 0.07, 0.01, 0, 0.07, (-1500.0,0.0,0.0),  0,   2,   1.0,    3.0, 0.0, 0.0, None),
          Level(0.08, 5, (0.0,0.0,100.0),  (150.0,200.0,100.0), 0.08, 0.01, 0, 0.08, (-1500.0,0.0,0.0),  0,   2,   1.0,    3.0, 0.0, 0.0, None),
          Level(0.1,  6, (0.0,0.0,100.0),  (150.0,200.0,100.0), 0.09, 0.01, 0, 0.09, (-1500.0,0.0,0.0),  0,   2,   1.0,    3.0, 0.0, 0.0, None),
          Level(0.12, 6, (0.0,0.0,100.0),  (150.0,200.0,100.0), 0.1,  0.02, 0, 0.1,  (-1500.0,0.0,0.0),  0,   3,   1.0,    3.0, 0.0, 0.0, None),
          Level(0.14, 7, (0.0,0.0,100.0),  (200.0,200.0,100.0), 0.11, 0.02, 0, 0.11, (-1500.0,0.0,0.0),  0,   3,   1.0,    3.0, 0.0, 0.0, (5, 25, 50)),
          Level(0.16, 8, (0.0,0.0,100.0),  (200.0,200.0,100.0), 0.12, 0.02, 0, 0.12, (-1500.0,0.0,0.0),  0,   3,   1.0,    2.0, 0.0, 0.0, (50, 5, 50)),
          Level(0.18, 9, (0.0,0.0,100.0),  (200.0,200.0,100.0), 0.13, 0.02, 0, 0.13, (-1500.0,0.0,0.0),  0,   3,   1.0,    2.0, 0.0, 0.0, (50, 25, 10)),
          Level(0.2, 10, (0.0,0.0,100.0),  (200.0,200.0,100.0), 0.14, 0.02, 0, 0.14, (-1500.0,0.0,0.0),  0,   3,   1.0,    2.0, 0.0, 0.0, (50, 10, 50)),

          Level(0.22, 2, (-50.0,0.0,200.0), (200.0,200.0,100.0),  0.1, 0.1, 1, 0.15, (-1000.0,0.0,0.0),  0,   1,   0.4,    4.0, 0.3, 0.0, None),
          Level(0.24, 3, (-50.0,0.0,200.0), (200.0,200.0,100.0),  0.1, 0.1, 1, 0.15, (-1000.0,0.0,0.0),  0,   1,   0.4,    4.0, 0.3, 0.0, None),
          Level(0.26, 4, (-50.0,0.0,200.0), (200.0,200.0,100.0),  0.12, 0.1, 1, 0.15, (-1000.0,0.0,0.0), 0,   2,   0.4,    4.0, 0.3, 0.0, None),
          Level(0.28, 5, (-50.0,0.0,200.0), (200.0,200.0,100.0),  0.12, 0.1, 1, 0.15, (-1000.0,0.0,0.0), 0,   2,   0.4,    4.0, 0.3, 0.0, None),
          Level(0.3,  6, (-50.0,0.0,200.0), (200.0,200.0,100.0),  0.12, 0.1, 1, 0.15, (-1000.0,0.0,0.0), 0,   2,   0.4,    3.0, 0.3, 0.0, None),
          Level(0.32, 7, (-50.0,0.0,100.0), (200.0,200.0,100.0),  0.13, 0.1, 1, 0.2, (-1000.0,0.0,0.0),  0,   3,   0.4,    3.0, 0.3, 0.0, (10, 25, 50)),
          Level(0.34, 8, (-50.0,0.0,100.0), (200.0,200.0,100.0),  0.13, 0.1, 1, 0.2, (-1000.0,0.0,0.0),  2,   3,   0.4,    3.0, 0.3, 0.0, (25, 10, 50)),
          Level(0.36, 9, (-50.0,0.0,100.0), (200.0,200.0,100.0),  0.14, 0.1, 1, 0.24, (-1000.0,0.0,0.0), 2,   3,   0.4,    3.0, 0.3, 0.0, (20, 25, 50)),
          Level(0.38, 10,(-50.0,0.0,100.0), (200.0,200.0,100.0),  0.15, 0.1, 1, 0.25, (-1000.0,0.0,0.0), 4,   3,   0.4,    2.0, 0.3, 0.0, (50, 10, 100)),
          Level(0.4,  10,(-50.0,0.0,100.0), (200.0,200.0,100.0),  0.16, 0.1, 1, 0.25, (-1000.0,0.0,0.0), 4,   3,   0.4,    2.0, 0.3, 0.0, (75, 10, 100)),

          Level(0.42, 2, (-100.0,0.0,200.0), (200.0,200.0,100.0), 0.6, 0.1, 2, 0.35, (-500.0,0.0,-200.0), 0,  1,   0.85,  8.0, 0.1, 0.4, None),
          Level(0.44, 3, (-100.0,0.0,200.0), (200.0,200.0,100.0), 0.6, 0.1, 2, 0.4, (-500.0,0.0,-200.0),  0,  1,   0.85,  8.0, 0.1, 0.4, None),
          Level(0.46, 4, (-100.0,0.0,200.0), (200.0,200.0,100.0), 0.6, 0.1, 2, 0.45, (-500.0,0.0,-200.0), 0,  1,   0.85,  8.0, 0.2, 0.4, None),
          Level(0.48, 5, (-100.0,0.0,200.0), (200.0,200.0,100.0), 0.61, 0.1, 2, 0.45, (-500.0,0.0,-200.0),0,  2,   0.85,  8.0, 0.2, 0.4, None),
          Level(0.5,  6, (-100.0,0.0,200.0), (300.0,200.0,100.0), 0.62, 0.1, 2, 0.45, (-500.0,0.0,-200.0),0,  2,   0.87,  8.0, 0.2, 0.4, None),
          Level(0.52, 7, (-100.0,0.0,200.0), (300.0,200.0,100.0), 0.63, 0.1, 2, 0.45, (-500.0,0.0,-200.0),0,  2,   0.88,  7.0, 0.2, 0.4, None),
          Level(0.54, 8, (-100.0,0.0,200.0), (300.0,200.0,100.0), 0.64, 0.1, 2, 0.55, (-500.0,0.0,-200.0),0,  3,   0.88,  7.0, 0.2, 0.4, (10, 10, 50)),
          Level(0.56, 9, (-100.0,0.0,200.0), (300.0,200.0,100.0), 0.7, 0.2, 2, 0.55, (-500.0,0.0,-200.0), 0,  3,   0.88,  6.0, 0.2, 0.5, (10, 50, 25)),
          Level(0.58, 9, (-100.0,0.0,200.0), (300.0,200.0,100.0), 0.75, 0.2, 2, 0.85, (-500.0,0.0,-200.0),0,  3,   0.92,  6.0, 0.2, 0.5, (100, 10, 50)),
          Level(0.6, 10, (-100.0,0.0,200.0), (300.0,200.0,100.0), 0.8, 0.2, 2, 0.85, (-500.0,0.0,-200.0), 0,  3,   0.95,  5.0, 0.3, 0.5, (100, 10, 100)),

          Level(0.62, 2, (-200.0,0.0,100.0), (100.0,200.0,300.0), 0.7, 0.3, 3, 0.85, (0.0,0.0,-500.0),   0,   1,   1.4,   6.0, 0.2, -0.1, None),
          Level(0.64, 3, (-200.0,0.0,100.0), (100.0,200.0,200.0), 0.72, 0.3, 3, 0.85, (0.0,0.0,-500.0),  0,   1,   1.4,   6.0, 0.2, -0.1, None),
          Level(0.66, 4, (-100.0,0.0,100.0), (100.0,200.0,200.0), 0.74, 0.3, 3, 0.9, (0.0,0.0,-500.0),   0,   1,   1.4,   6.0, 0.2, -0.1, None),
          Level(0.68, 5, (-100.0,0.0,100.0), (100.0,200.0,200.0), 0.76, 0.3, 3, 0.95, (0.0,0.0,-500.0),  0,   2,   1.4,   6.0, 0.2, -0.1, None),
          Level(0.7,  6, (-100.0,0.0,100.0), (100.0,200.0,200.0), 0.78, 0.3, 3, 0.95, (0.0,0.0,-500.0),  0,   2,   1.4,   6.0, 0.2, -0.1, (10, 10, 50)),
          Level(0.72, 7, (-100.0,0.0,100.0), (100.0,200.0,200.0), 0.8, 0.3, 3, 0.95, (0.0,0.0,-500.0),   1,   2,   1.4,   6.0, 0.2, -0.1, (10, 25, 50)),
          Level(0.74, 8, (-100.0,0.0,100.0), (100.0,200.0,200.0), 0.8, 0.3, 3, 1.05, (0.0,0.0,-500.0),   2,   3,   1.4,   6.0, 0.3, -0.1, (50, 10, 50)),
          Level(0.76, 8, (-100.0,0.0,100.0), (100.0,200.0,200.0), 0.82, 0.3, 3, 1.15, (0.0,0.0,-500.0),  2,   3,   1.4,   5.0, 0.3, -0.1, (25, 75, 50)),
          Level(0.78, 9, (-100.0,0.0,100.0), (100.0,200.0,300.0), 0.84, 0.3, 3, 1.25, (0.0,0.0,-500.0),  3,   3,   1.4,   5.0, 0.3, -0.1, (10, 25, 250)),
          Level(0.8, 10, (-100.0,0.0,100.0), (100.0,200.0,300.0), 0.86, 0.3, 3, 1.25, (0.0,0.0,-500.0),  4,   3,   1.4,   5.0, 0.3, -0.2, (125, 10, 200)),

          Level(0.82, 2, (-300.0,0.0,100.0), (100.0,200.0,100.0), 0.9, 0.1, 4, 1.00, (500.0,0.0,-500.0), 0,   1,   1.3,    5.0, 1.8, 12.8, None),
          Level(0.84, 3, (-300.0,0.0,100.0), (100.0,200.0,100.0), 0.9, 0.1, 4, 1.00, (500.0,0.0,-500.0), 0,   1,   1.3,    5.0, 1.8, 12.8, None),
          Level(0.86, 4, (-300.0,0.0,100.0), (100.0,200.0,100.0), 0.9, 0.1, 4, 1.00, (500.0,0.0,-500.0), 0,   1,   1.3,    4.0, 1.8, 12.8, None),
          Level(0.88, 5, (-300.0,0.0,100.0), (100.0,200.0,100.0), 0.9, 0.1, 4, 1.00, (500.0,0.0,-500.0), 0,   2,   1.2,    4.0, 1.8, 12.8, (10, 10, 50)),
          Level(0.9,  6, (-300.0,0.0,100.0), (100.0,200.0,100.0), 0.9, 0.1, 4, 1.00, (500.0,0.0,-500.0), 0,   2,   1.2,    4.0, 1.8, 12.8, (25, 25, 50)),
          Level(0.92, 7, (-300.0,0.0,100.0), (100.0,200.0,100.0), 0.9, 0.1, 4, 1.00, (500.0,0.0,-500.0), 0,   2,   1.2,    4.0, 1.8, 12.8, (40, 50, 25)),
          Level(0.94, 8, (-300.0,0.0,100.0), (100.0,200.0,100.0), 0.9, 0.1, 4, 1.00, (500.0,0.0,-500.0), 1,   3,   1.2,    4.0, 1.8, 12.8, (25, 10, 100)),
          Level(0.96, 9, (-300.0,0.0,100.0), (100.0,200.0,100.0), 0.9, 0.1, 4, 1.00, (500.0,0.0,-500.0), 2,   3,   1.1,    4.0, 1.8, 12.8, (50, 250, 50)),
          Level(0.98, 10,(-300.0,0.0,100.0), (100.0,200.0,100.0), 0.9, 0.1, 4, 1.00, (500.0,0.0,-500.0), 3,   3,   1.1,    4.0, 1.8, 12.8, (10, 125, 250)),
          Level(1.0,  10,(-300.0,0.0,100.0), (100.0,200.0,100.0), 0.9, 0.1, 4, 1.00, (500.0,0.0,-500.0), 3,   3,   1.1,    4.0, 1.8, 12.8, (200, 20, 200))
         ]
