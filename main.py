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
from dust import Dust
import os, pickle, glob

SHOOT = 0
RECHARGE = 1
N_FRAMES = 3600 #120s at 30fps
FLASH_FRAMES = 120
RECHARGE_LEVEL = 0.1
SHOOT_LEVEL = 0.9
MAX_DIST = 600.0
MIN_DIST = 4.0

########################################################################
class Main(object):
  # Setup display and initialise pi3d
  DISPLAY = pi3d.Display.create(x=250, y=100, far=10000, frames_per_second=30.0)
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
  cloudimg = pi3d.Texture('textures/earth_clouds.png', blend=True)
  earthimg = pi3d.Texture('textures/world_map.jpg')
  moonimg = pi3d.Texture('textures/moon.jpg')
  targimg = pi3d.Texture('textures/target.png', blend=True)
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
  ##### meters
  w, h = DISPLAY.width, DISPLAY.height
  score_meter = Meter(matsh, CAMERA2D, -w/2.3, w*0.05, DISPLAY.height, value=0.0)
  energy_meter = Meter(matsh, CAMERA2D, w/2.3, w*0.05, DISPLAY.height, value=0.0)
  ##### strings
  font = pi3d.Pngfont('fonts/Arial2.png', (200, 30, 10, 255))
  font.blend = True
  font2 = pi3d.Pngfont('fonts/Arial2.png', (10, 200, 100, 255))
  font2.blend = True
  default_string = pi3d.String(camera=CAMERA2D, font=font, string='RECHARGE',
                          is_3d=False, y=DISPLAY.height / 2.0 - 50.0, size=0.4)
  default_string.set_shader(flatsh)
  q_text = default_string
  s_text = default_string
  flash_count = 0
  ##### avatar camera
  rot = 0.0
  tilt = 0.0
  x, y, z = 0.0, 0.0, 0.0
  dx, dy, dz = 0.0, 0.0, 0.0

  go_speed = 0.2

  mode = SHOOT # 0 is shooting mode, 1 is recharge mode


#####----------------------------#####-----------------------------#####
  def score_mod(self, amount):
    ''' utility function to change score and flash up score and delta
    '''
    self.score += amount
    if self.score > 1.0:
      self.score = 1.0
    elif self.score < 0.0:
      self.score = 0.0
    self.score_meter.change_reading(self.score)
    font = self.font if amount < 0 else self.font2
    self.s_text = pi3d.String(camera=self.CAMERA2D, font=font,
                  string='{:,} >>{:,}<<'.format(int(1000000 * amount), int(1000000 * self.score)),
                  is_3d=False, y=-self.DISPLAY.height / 2.0 + 50.0, size=0.4)
    self.s_text.set_shader(self.flatsh)
    self.flash_count = 0
    

#####----------------------------#####-----------------------------#####
  def get_level(self):
    ''' utility function to get level from current score
    '''
    #for l in self.levels:
    #  if self.score >= l.minv and self.score <= l.maxv:
    #    return l
    return self.levels[min(self.q_pointer, len(self.levels)) - 1]


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
        if not (a.hit and a.explode_seq > 100): # an asteroid hasn't been hit or it's still exploding
          dist = ((a.loc[0] - self.x) ** 2 + (a.loc[1] - self.y) ** 2 + (a.loc[2] - self.z) ** 2) ** 0.5
          if dist  > MAX_DIST: # too far, kill it off NB directional
            a.hit = True
          elif dist < MIN_DIST:
            self.score_mod(-0.005)
            a.hit = True
            a.explode_seq = 101
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

    NB this sets various variables so needs to be run before main loop and check()
    '''
    with open('game.ini', 'wb') as fp: #save status
      saved_status = {'score': self.score, 'energy':self.energy,
                        'questions':self.questions, 'q_pointer':self.q_pointer}
      pickle.dump(saved_status, fp)
    self.frame_count = 0
    self.q_number = -1 # also use as flag indicate actually asking q
    self.level = self.get_level()
    if self.mode == SHOOT:
      (self.x, self.y, self.z) = (self.level.start_location)
      self.asteroids = []
      for i in range(self.level.num):
        a = self.asteroid_stock[i]
        a.launch(self.shinesh, self.rockimg, self.level.start_loc, self.level.start_range,
                (self.x, self.y, self.z), self.level.speed, self.level.speed_range,
                self.level.threshold)
        self.asteroids.append(a)
      if self.level.dust:
        self.dust = Dust(self.matsh, self.level.dust)
        self.dust.launch(self.level.start_loc, self.level.start_range, (self.x, self.y, self.z),
                  self.level.speed, self.level.speed_range)
      else:
        self.dust = None
      self.go_speed = self.level.go_speed
      self.q_text = self.default_string
      self.missile_pointer = 0
      self.num_missiles = self.level.num_missiles
      self.missile = self.level.missile
    else: # ask recharge questions
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
    if self.dust:
      self.dust.draw()
      self.dust.move()
      if (self.frame_count % 10) == 0 and self.dust.test_hit((self.x, self.y, self.z)):
        self.score_mod(-0.0025)
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
    if self.flash_count < FLASH_FRAMES:
      self.s_text.draw()
      self.flash_count += 1
    self.target.draw()

    ##### get input for direction and firing ###########################
    fire = False
    jump = False
    if PLATFORM == PLATFORM_ANDROID: # android <<<<<<<<<<<<<<<<<<<<<<<<<
      if self.DISPLAY.android.screen.moved:
        self.rot -= self.DISPLAY.android.screen.touch.dx * 0.25
        self.tilt += self.DISPLAY.android.screen.touch.dy * 0.25
        self.DISPLAY.android.screen.moved = False
        self.DISPLAY.android.screen.tapped = False
      elif self.DISPLAY.android.screen.tapped:
        fire = True
        self.DISPLAY.android.screen.tapped = False
        if self.DISPLAY.android.screen.touch.sx > 0.9 and self.DISPLAY.android.screen.touch.sy > 0.8:
          jump = True
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
        if k==ord(' '):  #key space
          fire = True
        elif k==ord('x'): #x key
          jump = True
        elif k==27:  #Escape key
          return False
      b = self.mouse.button_status()
      if b == self.mouse.LEFT_BUTTON:
        fire = True

    ##### act on results of input ######################################
    if jump:
      self.q_pointer = (self.q_pointer + 5) % len(questions)
      self.reset()
    if fire:
      if self.q_number > -1: # shooting at questions
        self.level = self.levels[0]
      self.missiles[self.missile][self.missile_pointer].launch([self.x, self.y, self.z],
              [self.dx / self.go_speed, self.dy / self.go_speed, self.dz / self.go_speed],
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
              rng = 1.0 + (((a.loc[0] - self.x) ** 2 + (a.loc[1] - self.y) ** 2 + (a.loc[2] - self.z) ** 2) ** 0.5) / 25.0
              score = 0.0005 * (1.0 - 0.5 / (0.5 + dist / a.threshold) / rng)
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
      while self.pi3dloop(0.0):
        pass
      self.keys.close()
      self.mouse.stop()

    self.DISPLAY.stop()

#####----------------------------#####-----------------------------#####
#####----------------------------#####-----------------------------#####

Main().run() #create an instance of Main() then run the run() method
