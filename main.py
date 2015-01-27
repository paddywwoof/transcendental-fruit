#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals
''' game to learn tables
'''
import demo
import random
import pi3d
from pi3d.constants import *
from asteroid import Asteroid
from missile import Missile
from questions import Question, questions
from meter import Meter

########################################################################
########################################################################
class Main(object):
  # Setup display and initialise pi3d
  DISPLAY = pi3d.Display.create(x=50, y=50, far=4000)
  ##### cameras
  CAMERA = pi3d.Camera()
  CAMERA2D = pi3d.Camera(is_3d=False)
  ##### shaders
  shader = pi3d.Shader('uv_bump')
  shinesh = pi3d.Shader('uv_reflect')
  flatsh = pi3d.Shader('uv_flat')
  matsh = pi3d.Shader('mat_flat')
  ##### textures
  bumpimg = pi3d.Texture('textures/moon_nm.jpg')
  reflimg = pi3d.Texture('textures/stars.jpg')
  rockimg = pi3d.Texture('textures/rock1.jpg')
  starimg = pi3d.Texture('textures/space1.jpg', flip=True)
  explimg = pi3d.Texture('models/ast_expl.png')
  ans108img = pi3d.Texture('textures/108.jpg', flip=True)
  ans63img = pi3d.Texture('textures/63.jpg', flip=True)
  ##### environment sphere
  sphere = pi3d.Sphere(radius=2000.0, rx=180, invert=True)
  sphere.set_draw_details(flatsh, [starimg])
  ##### asteroids
  asteroids = []
  for i in range(5):
    a = Asteroid(bumpimg, reflimg, explimg, 15.0)
    #a.launch(shinesh, rockimg, [0.0, 0.0, 400.0], [400.0, 300.0, 350.0],
    #                  [0.0, 0.0, 0.0], 0.2, 0.2)
    if i == 0:
      teximg = ans108img
    elif i == 1:
      teximg = ans63img
    else:
      teximg = rockimg
    a.launch(shinesh, teximg, [0.0, 0.0, 100.0], [200.0, 100.0, 5.0],
                      [0.0, 0.0, 0.0], 0.05, 0.02)
    asteroids.append(a)
  ##### missile
  missile = Missile(0, bumpimg, reflimg, shinesh)
  ##### meters
  energy = 0.7
  score = 0.1
  score_meter = Meter(matsh, CAMERA2D, -DISPLAY.width/2.0+60, 60.0, DISPLAY.height, value=score)
  energy_meter = Meter(matsh, CAMERA2D, DISPLAY.width/2.0-60, 60.0, DISPLAY.height, value=energy)

  #avatar camera
  rot = 0.0
  tilt = 0.0
  xm = 0.0
  zm = 0.0
  ym = 0.0

  go_flag = False
  go_speed = 0.2

  def pi3dloop(self, dt):
    self.DISPLAY.loop_running()
    self.CAMERA.reset()
    self.CAMERA.rotate(self.tilt, self.rot, 0)
    self.CAMERA.position((self.xm, self.ym, self.zm))
    self.sphere.position(self.xm, self.ym, self.zm)

    # for opaque objects it is more efficient to draw from near to far as the
    # shader will not calculate pixels already concealed by something nearer
    self.sphere.draw()
    for a in self.asteroids:
      a.draw()
      a.move()
    self.score_meter.draw()
    self.energy_meter.draw()

    fire = False
    if pi3d.PLATFORM == PLATFORM_ANDROID: #*****************************
      if self.DISPLAY.android.screen.moved:
        self.rot -= self.DISPLAY.android.screen.touch.dx * 0.25
        self.tilt += self.DISPLAY.android.screen.touch.dy * 0.25
        self.DISPLAY.android.screen.moved = False
        self.DISPLAY.android.screen.tapped = False
      elif self.DISPLAY.android.screen.tapped:
        self.go_speed *= 1.5
        self.DISPLAY.android.screen.tapped = False
      elif self.DISPLAY.android.screen.double_tapped:
        self.go_flag = not self.go_flag
        fire = True
        self.DISPLAY.android.screen.double_tapped = False
    else:
      mx, my = self.mouse.position()

      #if mx>display.left and mx<display.right and my>display.top and my<display.bottom:
      self.rot -= (mx - self.omx) * 0.2
      self.tilt += (my - self.omy) * 0.2
      self.omx = mx
      self.omy = my

      #Press ESCAPE to terminate
      k = self.keys.read()
      if k >-1:
        if k==ord('w'):  #key W
          self.go_flag = not self.go_flag
          fire = True
        elif k==27:  #Escape key
          return False

    if fire:
      self.missile.launch([self.xm, self.ym, self.zm], self.CAMERA.mtrx,
                          0.5, self.asteroids)
      self.energy -= 0.1
      self.energy_meter.change_reading(self.energy)

    if self.go_flag:
      self.xm += self.CAMERA.mtrx[0, 3] * self.go_speed
      self.ym += self.CAMERA.mtrx[1, 3] * self.go_speed
      self.zm += self.CAMERA.mtrx[2, 3] * self.go_speed
      self.missile.draw()
      self.missile.move()
      i, dist = self.missile.test_hits()
      if i > -1:
        self.go_flag = False
        if self.asteroids[i].test_hit(dist):
          self.score += 0.1
          self.score_meter.change_reading(self.score)

    else:
      self.go_speed = 0.2
    return True

  def run(self):
    if pi3d.PLATFORM == PLATFORM_ANDROID: #*****************************
      self.DISPLAY.android.set_loop(self.pi3dloop)
      self.DISPLAY.android.run()
    else:
      # Fetch key presses
      self.keys = pi3d.Keyboard()
      self.mouse = pi3d.Mouse(restrict = False)
      self.mouse.start()
      self.omx, self.omy = self.mouse.position()
      while self.pi3dloop(0.0):
        pass
      self.keys.close()
      self.mouse.stop()
        
    self.DISPLAY.stop()

Main().run() #create an instance of Main() then run the method
