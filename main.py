#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals
''' game to learn tables
'''
import demo
import random
import pi3d
from pi3d.constants import PLATFORM, PLATFORM_ANDROID
from asteroid import Asteroid
from missile import Missile
from questions import Question, questions
from meter import Meter
from level import Level, levels
import os, pickle, glob

SHOOT = 0
RECHARGE = 1
N_FRAMES = 7200 #120s at 60fps
RECHARGE_LEVEL = 0.1
SHOOT_LEVEL = 0.9
MAX_DIST = 300

########################################################################
class Main(object):
  # Setup display and initialise pi3d
  DISPLAY = pi3d.Display.create(x=50, y=50, far=10000, frames_per_second=30.0)
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
  starimg = pi3d.Texture('textures/space1.jpg', flip=True)
  explimg = pi3d.Texture('models/ast_expl.png')
  cloudimg = pi3d.Texture("textures/earth_clouds.png", blend=True)
  earthimg = pi3d.Texture("textures/world_map.jpg")
  moonimg = pi3d.Texture("textures/moon.jpg")
  ansimg = {}
  fnames = glob.glob('textures/???.jpg')
  for f in fnames:
    ansimg[int(f[9:12])] = pi3d.Texture(f, flip=True)
  ##### environment sphere
  sphere = pi3d.Sphere(radius=4000.0, rz=90, invert=True)
  sphere.set_draw_details(flatsh, [starimg])
  sphere.set_fog((0.0, 0.0, 0.0, 1.0), 12000)
  ##### earth
  earth = pi3d.Sphere(radius=1000.0, slices=16, sides=32)
  earth.set_draw_details(shader, [earthimg])
  earth.set_fog((0.0, 0.0, 0.0, 1.0), 12000)
  earth.positionX(2400.0)
  ##### clouds
  clouds = pi3d.Sphere(radius=1020.0, slices=16, sides=32)
  clouds.set_draw_details(shader, [cloudimg])
  clouds.set_fog((0.0, 0.0, 0.0, 1.0), 12000)
  clouds.positionX(2400.0)
  ##### moon
  moon = pi3d.Sphere(radius=500.0, slices=24, sides=24)
  moon.set_draw_details(shader, [moonimg])
  moon.set_fog((0.0, 0.0, 0.0, 1.0), 12000)
  moon.positionX(-2400.0)
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
  for i in range(1):
    missiles.append([]) # i.e. list of lists
    missiles[i].append(Missile(i, bumpimg, reflimg, shinesh)) #zeroth is prototype
    for j in range(4):
      missiles[i].append(Missile(i, bumpimg, reflimg, shinesh, clone=missiles[i][0]))
  ##### meters
  w, h = DISPLAY.width, DISPLAY.height
  score_meter = Meter(matsh, CAMERA2D, -w/2.3, w*0.05, DISPLAY.height, value=0.0)
  energy_meter = Meter(matsh, CAMERA2D, w/2.3, w*0.05, DISPLAY.height, value=0.0)
  ##### strings
  font = pi3d.Pngfont('fonts/Arial2.png', (200, 30, 10, 255))
  font.blend = True
  default_string = pi3d.String(camera=CAMERA2D, font=font, string='RECHARGE',
                          is_3d=False, y=DISPLAY.height / 2.0 - 50.0, size=0.4)
  default_string.set_shader(flatsh)
  q_text = default_string
  ##### avatar camera
  rot = 0.0
  tilt = 0.0
  x = 0.0
  z = 0.0
  y = 0.0

  go_speed = 0.2

  mode = SHOOT # 0 is shooting mode, 1 is recharge mode
  timer = 0 # count up to N_FRAMES or all asteroids hit in shooting mode or correct asteroids hit in recharge mode

#####----------------------------#####-----------------------------#####
  def get_level(self):
    ''' utility function to get level from current score
    '''
    for l in self.levels:
      if self.score >= l.minv and self.score <= l.maxv:
        return l
    return self.levels[-1] # at max level

#####----------------------------#####-----------------------------#####
  def check(self):
    ''' timer, asteroid hits, question/answer
    '''
    if self.mode == SHOOT and self.energy < RECHARGE_LEVEL:
      self.mode = RECHARGE
    elif self.mode == RECHARGE and self.energy > SHOOT_LEVEL:
      self.mode = SHOOT
    self.frame_count += 1
    if self.frame_count > N_FRAMES: # out of time
      return True
    else:
      all_hit = True
      correct_answer = False
      for a in self.asteroids:
        if not a.hit: # an asteroid hasn't been hit
          if  self.z - a.loc[2] > MAX_DIST: # too far, kill it off NB directional
            a.hit = True
          else:
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
    '''
    with open('game.ini', 'w') as fp: #save status
      saved_status = {'score': self.score, 'energy':self.energy,
                        'questions':self.questions, 'q_pointer':self.q_pointer}
      pickle.dump(saved_status, fp)
    self.frame_count = 0
    if self.mode == SHOOT:
      level = self.get_level()
      (self.x, self.y, self.z) = (level.start_location)
      self.asteroids = []
      for i in range(level.num):
        a = self.asteroid_stock[i]
        a.launch(self.shinesh, self.rockimg, level.start_loc, level.start_range,
                (self.x, self.y, self.z), level.speed, level.speed_range)
        self.asteroids.append(a)
      self.go_speed = level.go_speed
      self.q_text = self.default_string
      self.missile_pointer = 0
      self.num_missiles = level.num_missiles
      self.missile = level.missile
    else: # ask recharge questions
      self.q_number = -1
      all_good = True
      for i, q in enumerate(self.questions[:self.q_pointer]): #restricted list
        ratio = q.right / (q.right + q.wrong + 0.5)
        if ratio < 0.75:
          self.q_number = i
          break
        elif ratio < 0.85:
          all_good = False
      if all_good: #add a new question for next time
        self.q_pointer += 1
        if self.q_pointer >= (len(self.questions) - 1):
          self.q_pointer = len(self.questions) - 1
      if self.q_number == -1: #all over threshold choose a random one
        self.q_number = random.randint(0, self.q_pointer - 1)
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
              threshold=5.0, correct_answer=(i == 0))
        self.asteroids.append(a)
      #set missile
      self.go_speed = 0.01
   
#####----------------------------#####-----------------------------#####
  def __init__(self):
    ''' need an instance to do initial settings with reset
    '''
    ##### load saved game state
    if os.path.isfile('game.ini'):
      with open('game.ini', 'r') as fp:
        saved_status = pickle.load(fp)
        self.score = saved_status['score']
        self.energy = saved_status['energy']
        self.questions = saved_status['questions']
        self.q_pointer = saved_status['q_pointer']
    else:
      self.score = 0.0
      self.energy = 1.0
      self.questions = questions #from imported questions
      self.q_pointer = 1 #number to slice with not really pointer
    self.mode = SHOOT
    self.q_number = 0 #set when question asked
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

    if self.check():
      self.reset()

    # have to draw from far to near for transparency
    self.sphere.draw()
    for a in self.asteroids:
      a.draw()
      a.move()
    self.earth.draw()
    self.moon.draw()
    self.clouds.draw()
    self.score_meter.draw()
    self.energy_meter.draw()
    if self.mode == RECHARGE:
      self.q_text.draw()

    ##### get input for direction and firing ###########################
    fire = False
    if PLATFORM == PLATFORM_ANDROID: # android <<<<<<<<<<<<<<<<<<<<<<<<<
      if self.DISPLAY.android.screen.moved:
        self.rot -= self.DISPLAY.android.screen.touch.dx * 0.25
        self.tilt += self.DISPLAY.android.screen.touch.dy * 0.25
        self.DISPLAY.android.screen.moved = False
        self.DISPLAY.android.screen.tapped = False
      elif self.DISPLAY.android.screen.tapped:
        fire = True
        self.DISPLAY.android.screen.tapped = False
      #  self.DISPLAY.android.screen.double_tapped = False
    else: # other platforms >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
      mx, my = self.mouse.position()

      self.rot -= (mx - self.omx) * 0.2
      self.tilt += (my - self.omy) * 0.2
      self.omx = mx
      self.omy = my

      #Press ESCAPE to terminate
      k = self.keys.read()
      if k >-1:
        if k==ord('w'):  #key W
          fire = True
        elif k==27:  #Escape key
          return False

    ##### act on results of input ######################################
    if fire:
      self.missiles[self.missile][self.missile_pointer].launch([self.x, self.y, self.z],
                                  self.CAMERA.mtrx, 0.5, self.asteroids)
      self.energy -= 0.05
      self.energy_meter.change_reading(self.energy)
      self.missiles[self.missile][self.missile_pointer].flag = True
      self.missile_pointer = (self.missile_pointer + 1) % self.num_missiles

    self.x += self.CAMERA.mtrx[0, 3] * self.go_speed
    self.y += self.CAMERA.mtrx[1, 3] * self.go_speed
    self.z += self.CAMERA.mtrx[2, 3] * self.go_speed
    for m in self.missiles[self.missile][0:self.num_missiles]:
      if m.flag:
        m.draw()
        m.move()
        i, dist = m.test_hits()
        if i > -1:
          m.flag = False
          if self.asteroids[i].test_hit(dist):
            if self.mode == SHOOT:
              self.score += 0.025
              if self.score > 1.0:
                self.score = 1.0
              self.score_meter.change_reading(self.score)
            else: # questioning
              if self.asteroids[i].correct_answer:
                self.energy += 0.3
                if self.energy > 1.0:
                  self.energy = 1.0
                self.energy_meter.change_reading(self.energy)
                self.questions[self.q_number].right += 1
              else:
                self.questions[self.q_number].wrong += 1

    return True

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
      while self.pi3dloop(0.0):
        pass
      self.keys.close()
      self.mouse.stop()
        
    self.DISPLAY.stop()

Main().run() #create an instance of Main() then run the run() method
