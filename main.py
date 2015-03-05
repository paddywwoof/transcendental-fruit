#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals
''' game to learn tables
'''
import demo
import random
import pi3d
from pi3d.constants import PLATFORM, PLATFORM_ANDROID
from asteroid import Asteroid, EXPLODE_N
from missile import Missile
from questions import Question, questions
from meter import Meter
from level import Level, levels, level_names
from dust import Dust

import os, pickle, glob, math

SHOOT = 0
RECHARGE = 1
N_FRAMES = 2000 #120s at 30fps
FLASH_FRAMES = 120
RECHARGE_LEVEL = 0.1
SHOOT_LEVEL = 0.9

# adjust following to make game nicely balanced
MAX_DIST = 600.0
MIN_DIST = 4.0
MAX_DUST_DAMAGE = 0.1
DUST_DAMAGE = -0.005
ESCAPER = -0.025
BUMP = -0.30
TOP_UP = 0.04 # per good asteroid

########################################################################
class Main(object):
  # Setup display and initialise pi3d
  DISPLAY = pi3d.Display.create(x=100, y=100, far=15000, frames_per_second=30.0)
  ##### cameras
  CAMERA = pi3d.Camera()
  CAMERA2D = pi3d.Camera(is_3d=False)
  ##### shaders
  shader = pi3d.Shader('uv_light')
  shinesh = pi3d.Shader('uv_reflect')
  flatsh = pi3d.Shader('uv_flat')
  matsh = pi3d.Shader('mat_flat')
  ##### textures
  bumpimg = pi3d.Texture('textures/moon_nm.jpg')
  reflimg = pi3d.Texture('textures/stars.jpg')
  rockimg = pi3d.Texture('textures/rock1.jpg')
  goodimg = pi3d.Texture('textures/rock2.jpg')
  starimg = pi3d.Texture('textures/space1.jpg', flip=True)
  explimg = pi3d.Texture('models/ast_expl.png')
  cloudimg = pi3d.Texture('textures/earth_clouds.png', blend=True)
  earthimg = pi3d.Texture('textures/world_map.jpg')
  moonimg = pi3d.Texture('textures/moon.jpg')
  targimg = pi3d.Texture('textures/target.png', blend=True)
  magmaimg = pi3d.Texture('textures/magma.jpg')
  ansimg = {}
  fnames = glob.glob('textures/???.jpg')
  for f in fnames:
    ansimg[int(f[9:12])] = pi3d.Texture(f, flip=True)
  ##### environment sphere
  sphere = pi3d.Sphere(radius=4000.0, rz=90, invert=True)
  sphere.set_draw_details(flatsh, [starimg])
  sphere.set_fog((0.0, 0.0, 0.0, 1.0), 15000)
  ##### earth
  earth = pi3d.Sphere(radius=1000.0, slices=16, sides=32)
  earth.set_draw_details(shader, [earthimg])
  earth.set_fog((0.0, 0.0, 0.0, 1.0), 15000)
  earth.positionX(2400.0)
  earth.rotateToY(360.0 * random.random())
  ##### clouds
  clouds = pi3d.Sphere(radius=1020.0, slices=16, sides=32)
  clouds.set_draw_details(shader, [cloudimg])
  clouds.set_fog((0.0, 0.0, 0.0, 1.0), 15000)
  clouds.positionX(2400.0)
  ##### moon
  moon = pi3d.Sphere(radius=500.0, slices=24, sides=24)
  moon.set_draw_details(shader, [moonimg])
  moon.set_fog((0.0, 0.0, 0.0, 1.0), 15000)
  moon.positionX(-2000.0)
  ##### target
  target = pi3d.Sprite(w=64, h=64, camera=CAMERA2D)
  target.set_draw_details(flatsh, [targimg])
  ##### levels
  levels = levels
  ##### asteroids
  asteroid_stock = [] #stock of available asteroids to use
  asteroids = [] #list of 'active' asteroids
  asteroid_stock.append(Asteroid(bumpimg, reflimg, explimg)) #zeroth is prototype to clone
  for i in range(9):
    asteroid_stock.append(Asteroid(bumpimg, reflimg, explimg, clone=asteroid_stock[0]))
  ##### missile
  missiles = []
  for i in range(5):
    missiles.append([]) # i.e. list of lists
    missiles[i].append(Missile(i, bumpimg, reflimg, shader)) #zeroth is prototype
    for j in range(4):
      missiles[i].append(Missile(i, bumpimg, reflimg, (shinesh if i < 2 else shader), clone=missiles[i][0]))
  ##### dust
  dust = None
  dust_damage_tally = 0
  ##### meters
  w, h = DISPLAY.width, DISPLAY.height
  health_meter = Meter(matsh, CAMERA2D, -w/2.3, w*0.05, DISPLAY.height, value=0.0)
  energy_meter = Meter(matsh, CAMERA2D, w/2.3, w*0.05, DISPLAY.height, value=0.0)
  ##### skip button
  skip_button = pi3d.Triangle(camera=CAMERA2D, x=w*0.45, y=h*0.4, z=1.0,
                              corners=((0, 0), (0, h*0.1),(w*0.05,h*0.05)))
  skip_button.set_material((0.7, 0.8, 1.0))
  skip_button.set_shader(matsh)
  skip_button.set_alpha(0.1)
  ##### strings
  font = pi3d.Pngfont('fonts/Arial2.png', (200, 30, 10, 255))
  font.blend = True
  font2 = pi3d.Pngfont('fonts/Arial2.png', (10, 200, 100, 255))
  font2.blend = True
  default_string = pi3d.String(camera=CAMERA2D, font=font, string='RECHARGE',
                          is_3d=False, y=DISPLAY.height / 2.0 - 50.0, size=0.4)
  default_string.set_shader(flatsh)
  q_text = default_string
  s_text = None
  flash_count = 0
  ##### end sequence
  magma = pi3d.Sphere(radius=900.0, slices=16, sides=32)
  magma.set_draw_details(shader, [magmaimg])
  magma.set_fog((0.0, 0.0, 0.0, 1.0), 15000)
  magma.set_alpha(0.45)
  end_count = -1
  magma.positionX(2400.0)
  ##### avatar camera
  rot = 0.0
  tilt = 0.0
  drot = 0.0 # rate of rot, for touch screen 'gliding'
  dtilt = 0.0
  x, y, z = 0.0, 0.0, 0.0
  dx, dy, dz = 0.0, 0.0, 0.0

  go_speed = 0.2

  mode = SHOOT # 0 is shooting mode, 1 is recharge mode


#####----------------------------#####-----------------------------#####
  def endgame(self):
    # write score to history if in top 5
    self.l_number = 0 #start as 0 each time it runs
    self.health = 1.0 #start off full health each time
    self.scores.append(self.score)
    self.scores.sort(reverse=True)
    self.scores = self.scores[0:5] # cut off the first 5
    #self.score = 0 set this to zero after end of world sequence!
    self.q_text = self.high_score_text()
    self.end_count = 500
    self.x, self.y, self.z = -2300, 50, 590.0
    self.CAMERA.position((self.x, self.y, self.z))
    self.tilt, self.rot = self.CAMERA.point_at([self.earth.x(), self.earth.y(), self.earth.z()])

    

#####----------------------------#####-----------------------------#####
  def high_score_text(self):
    text = '\n'.join(['{:,}'.format(i) for i in self.scores])
    pi3d_string = pi3d.String(camera=self.CAMERA2D, font=self.font,
                  string=text, justify='c', is_3d=False, y=50.0, x=100.0, size=0.3)
    pi3d_string.set_shader(self.flatsh)
    return pi3d_string


#####----------------------------#####-----------------------------#####
  def score_mod(self, amount):
    ''' utility function to change score and flash up score and delta
    '''
    if amount < 0: # this is a reduction in health
      font = self.font # red
      self.health += amount
      amount = -100 * amount
      if self.health < 0.0:
        self.endgame()
      self.health_meter.change_reading(self.health)
      prefix = '%'
    else:
      self.score += amount
      font = self.font2 # green
      prefix = '+'
    self.s_text = pi3d.String(camera=self.CAMERA2D, font=font,
                  string='{}{:,}'.format(prefix, amount),
                  is_3d=False, y=-self.DISPLAY.height / 2.0 + 50.0, size=0.6)
    self.s_text.set_shader(self.flatsh)
    self.flash_count = 0
    

#####----------------------------#####-----------------------------#####
  def get_level(self):
    ''' utility function to get level from current score and question
    '''
    return self.levels[min(self.l_number, len(self.levels) - 1)]


#####----------------------------#####-----------------------------#####
  def check(self):
    ''' timer, asteroid hits, question/answer
    '''
    if self.mode == SHOOT and self.energy < RECHARGE_LEVEL:
      #for m in self.missiles[self.missile]: # tidy any still travelling missiles
      #  m.flag = False
      self.mode = RECHARGE
      if (self.l_number % 10) != 1:
        self.q_text = self.default_string
    elif self.mode == RECHARGE and self.energy > SHOOT_LEVEL:
      self.mode = SHOOT
    self.frame_count += 1
    if self.frame_count > N_FRAMES: # out of time
      return True
    else:
      all_hit = True
      correct_answer = False
      for a in self.asteroids:
        if not (a.hit and a.explode_seq > EXPLODE_N): # an asteroid hasn't been hit or it's still exploding
          dist = ((a.loc[0] - self.x) ** 2 + (a.loc[1] - self.y) ** 2 + (a.loc[2] - self.z) ** 2) ** 0.5
          if dist  > MAX_DIST or self.frame_count == N_FRAMES: # too far or out of time, kill it off
            if a.good: # a good asteroid has got through, hurrah
              self.health += TOP_UP
            a.hit = True
            a.explode_seq = 101
            self.score_mod(ESCAPER) # penalty for escaping asteroid -1.5%
          elif dist < MIN_DIST:
            self.score_mod(BUMP) # penalty for bumping into asteroid -30%
            a.hit = True
            a.explode_seq = 101
          elif not a.good:
            all_hit = False
        elif a.correct_answer: # asteroid hit and it was correct answer
          correct_answer = True
      if all_hit:
        return True
      if correct_answer:
        return True
      return False


#####----------------------------#####-----------------------------#####
  def reset(self):
    ''' put asteroids in start positions with correct textures etc.
    pass asteroid list to missile.

    NB this sets various variables so needs to be run before main loop and check()
    '''
    with open('game.ini', 'wb') as fp: #save status
      saved_status = {'scores': self.scores, 'energy':self.energy,
                    'questions':self.questions, 'q_pointer':self.q_pointer,
                    'score': self.score, 'l_number': self.l_number,
                    'health': self.health}
      pickle.dump(saved_status, fp)
    self.frame_count = 0
    self.q_number = -1 # also use as flag indicate actually asking q
    self.level = self.get_level()
    if self.mode == SHOOT: # - launch new set of target asteroids
      (self.x, self.y, self.z) = (self.level.start_location)
      self.asteroids = []
      for i in range(self.level.num):
        a = self.asteroid_stock[i]
        if i < self.level.num_good:
          tex = self.goodimg
          good = True
        else:
          tex = self.rockimg
          good = False
        a.launch(self.shinesh, tex, self.level.start_loc, self.level.start_range,
                (self.x, self.y, self.z), self.level.speed, self.level.speed_range,
                threshold=self.level.threshold, good=good)
        self.asteroids.append(a)
      if self.level.dust:
        self.dust = Dust(self.matsh, self.level.dust)
        self.dust.launch(self.level.start_loc, self.level.start_range, (self.x, self.y, self.z),
                  self.level.speed, self.level.speed_range)
        self.dust_damage_tally = 0
      else:
        self.dust = None
      self.go_speed = self.level.go_speed
      #self.q_text = self.default_string
      self.missile_pointer = 0
      self.num_missiles = self.level.num_missiles
      self.missile = self.level.missile
      self.l_number += 1
      if (self.l_number % 10) == 1:
        #self.health += TOP_UP # major recovery each progression to new missile
        self.q_text = pi3d.String(camera=self.CAMERA2D, font=self.font,
                          string='level ' + level_names[int((self.l_number - 1) / 10) % len(level_names)],
                          is_3d=False, y=self.DISPLAY.height / 2.0 - 50.0, size=0.4)
        self.q_text.set_shader(self.flatsh)
      else:
        self.health += 0.025 # heath boost each round 2.5%
      if self.health > 1.0:
        self.health = 1.0
    else: # ask recharge questions
      for a in self.asteroid_stock: # kill off any stray asteroids in case they get hit by a still travelling missile
        a.hit = True
      all_good = True
      self.dx = self.dy = self.dz = 0.0
      total = 0.0
      for i, q in enumerate(self.questions[:self.q_pointer]): #restricted list
        q.ratio = (q.wrong + 0.5) / (q.right + 0.5) #wrongness
        total += q.ratio
        if q.ratio > 0.25:
          all_good = False
      if all_good: #add a new question for next time
        self.q_pointer += 1
        if self.q_pointer >= (len(self.questions) - 1):
          self.q_pointer = len(self.questions) - 1
      #if self.q_number == -1: #all over threshold choose a random one
      r = random.uniform(0.0, total) # weight probability by q.ratio
      upto = 0.0
      for self.q_number, q in enumerate(self.questions[:self.q_pointer]):
        upto += q.ratio
        if (upto >= r):
           break
      question, ans = self.questions[self.q_number].make_qanda()
      self.q_text = pi3d.String(camera=self.CAMERA2D, font=self.font, string=question,
                            is_3d=False, y=self.DISPLAY.height / 2.0 - 50.0, size=0.4)
      self.q_text.set_shader(self.flatsh)
      ans_list = [ans] #add correct answer first
      while len(ans_list) < 5:
        poss_ans = random.choice(list(self.ansimg.keys()))
        if not (poss_ans in ans_list):
          ans_list.append(poss_ans)
      self.asteroids = []
      offset = random.randint(0, 4)
      for i, ans_num in enumerate(ans_list):
        a = self.asteroid_stock[i]
        a.launch(self.shinesh, self.ansimg[ans_num], (15.0 * ((i + offset) % 5) - 30.0, 0.0, 50.0),
              (8.0, 8.0, 2.0), (self.x, self.y, self.z), 0.03, 0.01,
              threshold=4.0, correct_answer=(i == 0))
        self.asteroids.append(a)
      #set missile
      self.go_speed = 0.01


#####----------------------------#####-----------------------------#####
  def __init__(self):
    ''' need an instance to do initial settings with reset
    '''
    ##### load saved game state
    if os.path.isfile('game.ini'):
      with open('game.ini', 'rb') as fp:
        saved_status = pickle.load(fp)
        self.scores = saved_status['scores']
        self.energy = saved_status['energy']
        self.questions = saved_status['questions']
        self.q_pointer = saved_status['q_pointer']
        self.score = saved_status['score']
        self.l_number = saved_status['l_number']
        self.health = saved_status['health']
    else:
      self.scores = []
      self.energy = 1.0
      self.questions = questions #from imported questions
      self.q_pointer = 1 #number to slice with, not really pointer
      self.score = 0
      self.l_number = 0
      self.health = 1.0 #start off full health each time
    #self.l_number = 39
    self.mode = SHOOT
    self.q_number = 0 #set when question asked
    #self.health = 1.0 #start off full health each time
    self.health_meter.change_reading(1.0)
    self.energy_meter.change_reading(1.0)
    self.s_text = self.high_score_text()
    self.s_text.set_shader(self.flatsh)
    self.reset()


#----############################-----#############################----#
#####----------------------------#####-----------------------------#####
#----############################-----#############################----#
  def pi3dloop(self, dt):
    self.DISPLAY.loop_running()
    self.CAMERA.reset()
    self.CAMERA.rotate(self.tilt, self.rot, 0)
    self.CAMERA.position((self.x, self.y, self.z))
    self.sphere.position(self.x, self.y, self.z)

    # have to draw from far to near for transparency
    self.sphere.draw()
    if (self.frame_count % 30) == 0:
      self.earth.rotateIncY(-0.07)
      self.clouds.rotateIncY(-0.11)
    self.earth.draw()
    self.moon.draw()
    self.clouds.draw()
    if self.end_count > 0: # end or world sequence
      end_text = "the END!.. "
      alpha = self.end_count / 500.0
      self.earth.set_alpha(alpha)
      self.clouds.set_alpha(alpha)
      self.magma.set_alpha(alpha)
      self.magma.draw()
      self.magma.translateX(-1.5)
      self.magma.rotateIncX(0.1)
      self.end_count -= 1
    elif self.end_count == 0: # reset end of world
      end_text = ""
      self.score = 0
      self.magma.positionX(2400)
      self.end_count = -1
      self.earth.set_alpha(1.0)
      self.clouds.set_alpha(1.0)
      self.reset()
    else: # normal drawing etc
      end_text = ""
      for a in self.asteroids:
        a.draw()
        a.move()
      self.health_meter.draw()
      if self.dust:
        self.dust.draw()
        self.dust.move()
        if ((self.frame_count % 10) == 0 and
             self.dust.test_hit((self.x, self.y, self.z)) and
             self.dust_damage_tally < MAX_DUST_DAMAGE):
               # to prevent destruction if going same direction as dust
          self.score_mod(DUST_DAMAGE) # hit by dust -0.5%
          self.dust_damage_tally += DUST_DAMAGE 
      self.energy_meter.draw()
      if self.mode == RECHARGE or (self.l_number % 10) == 1:
        self.q_text.draw()
      self.target.draw()
      self.skip_button.draw()

      if self.check():
        self.reset()

    if self.flash_count < FLASH_FRAMES:
      self.flash_count += 1
      self.s_text.translateY(-0.5)
    elif self.flash_count == FLASH_FRAMES:
      self.s_text = pi3d.String(camera=self.CAMERA2D, font=self.font2,
                    string='{}{:,}'.format(end_text, self.score),
                    is_3d=False, y=-self.DISPLAY.height / 2.0 + 50.0, size=0.4)
      self.s_text.set_shader(self.flatsh)
    self.s_text.draw()

    ##### get input for direction and firing ###########################
    fire = False
    jump = False
    cheat = False
    if PLATFORM == PLATFORM_ANDROID: # android <<<<<<<<<<<<<<<<<<<<<<<<<
      #self.skip_button.draw()
      scr = self.DISPLAY.android.screen # alias for brevity!
      if scr.touch and scr.touch.ud['down']: #still touching: damped
        damping = 0.0
      else:
        damping = 0.98 #low damping unless touch still down
        
      if scr.moved:
        damping = 0.65 #if moving use medium damping for speed multiplier
        sensitivity = 25.0
        self.drot -= scr.touch.dsx * sensitivity
        self.dtilt += scr.touch.dsy * sensitivity
        scr.moved = False
      elif scr.tapped or scr.double_tapped:
        fire = True
        scr.tapped = False
        scr.double_tapped = False
        if scr.touch.sx > 0.90 and scr.touch.sy > 0.8:
          jump = True
          if scr.previous_touch.ud['down'] and scr.previous_touch.sx > 0.9 and scr.previous_touch.sy < 0.2:
            cheat = True
      self.rot += self.drot
      self.tilt += self.dtilt
      self.drot *= damping
      self.dtilt *= damping
    else: # other platforms >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
      mx, my = self.mouse.position()

      self.rot -= (mx - self.omx) * 0.1
      self.tilt += (my - self.omy) * 0.1
      self.omx = mx
      self.omy = my

      #Press ESCAPE to terminate
      k = self.keys.read()
      if k >-1:
        if k==ord(' '):  #key space
          fire = True
        elif k==ord('x'): #x key
          jump = True
        elif k==ord('4'): #cheat
          jump = True
          cheat = True
        elif k==27:  #Escape key
          return False
      b = self.mouse.button_status()
      if b == self.mouse.LEFT_BUTTON:
        fire = True

    if self.tilt > 90:
      self.tilt = 90
    elif self.tilt < -90:
      self.tilt = -90
    ##### act on results of input ######################################
    if jump:
      #self.l_number = (self.l_number + 5) % len(questions)
      #self.reset()
      self.frame_count = N_FRAMES - 1 # go to final tidy up frame
      if cheat:
        self.score = 0
        self.health = 1.0
        self.energy = 1.0
    if fire:
      if self.q_number > -1: # shooting at questions
        self.level = self.levels[0]
      self.missiles[self.missile][self.missile_pointer].launch([self.x, self.y, self.z],
              self.CAMERA.mtrx[0:3, 3], #[self.dx / self.go_speed, self.dy / self.go_speed, self.dz / self.go_speed],
              self.level.missile_speed, self.asteroids, g_asteroid=self.level.g_asteroid,
              g_missile=self.level.g_missile)
      self.energy -= 0.05
      self.energy_meter.change_reading(self.energy)
      self.missiles[self.missile][self.missile_pointer].flag = True
      self.missile_pointer = (self.missile_pointer + 1) % self.num_missiles

    self.dx = self.dx * 0.95 + self.CAMERA.mtrx[0, 3] * self.go_speed * 0.05
    self.dy = self.dy * 0.95 + self.CAMERA.mtrx[1, 3] * self.go_speed * 0.05
    self.dz = self.dz * 0.95 + self.CAMERA.mtrx[2, 3] * self.go_speed * 0.05
    self.x += self.dx
    self.y += self.dy
    self.z += self.dz
    for m in self.missiles[self.missile][0:self.num_missiles]:
      if m.flag:
        m.draw()
        m.move()
        i, dist = m.test_hits()
        if i > -1:
          m.flag = False
          a = self.asteroids[i]
          if a.test_hit(dist):
            if self.q_number == -1: # not asking actual question so score
              rng = 1.0 + (((a.loc[0] - self.x) ** 2 + (a.loc[1] - self.y) ** 2 + (a.loc[2] - self.z) ** 2) ** 0.5) / 50.0
              score = int(2000 * (1.0 - 0.25 / (0.25 + dist / a.threshold) / rng))
              if a.good:
                score = -0.25 # penalty for hitting a good asteroid 25%
              self.score_mod(score)
            else: # questioning
              q = self.questions[self.q_number]
              if self.asteroids[i].correct_answer:
                self.energy += 0.3
                if self.energy > 1.0:
                  self.energy = 1.0
                self.energy_meter.change_reading(self.energy)
                q.right = q.right * 0.9 + 1.0 #exponential decay old scores
                q.wrong = q.wrong * 0.9
              else:
                q.right = q.right * 0.9
                q.wrong = q.wrong * 0.9 + 1.0

    return True

#####----------------------------#####-----------------------------#####
  def run(self):
    if PLATFORM == PLATFORM_ANDROID: # android <<<<<<<<<<<<<<<<<<<<<<<<<
      self.DISPLAY.android.set_loop(self.pi3dloop)
      self.DISPLAY.android.run()
    else: # other platforms >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
      # Fetch key presses
      self.keys = pi3d.Keyboard()
      self.mouse = pi3d.Mouse(restrict = False)
      self.mouse.start()
      self.omx, self.omy = self.mouse.position()
      while self.pi3dloop(0.0): # not using the argument kivy passes
        pass
      self.keys.close()
      self.mouse.stop()

    self.DISPLAY.stop()

#####----------------------------#####-----------------------------#####
#####----------------------------#####-----------------------------#####

Main().run() #create an instance of Main() then run the run() method
