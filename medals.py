#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

import demo
import pi3d
from math import radians, sin, cos
from pi3d.constants import PLATFORM, PLATFORM_ANDROID

R = 4.5
if PLATFORM != PLATFORM_ANDROID:
  ALT_TEXT = ["Z", "X", "SPACE", ""]
  TARGETS = [525, 425, 0.5, 0.95, 0.05]
else:
  ALT_TEXT = ["TAP top-left", "TAP top-right", "TAP",
              """Keeping touching stops your craft spinning
freely, you can then shoot accurately by tapping
with a different finger"""]
  TARGETS = [575, 475, 0.75, 0.90, 0.1]
M_TEXT = [
"""7 x Champion

Master the most difficult part
of the multiplication tables""",

"""Heavy Weight Champion

Cope with the top end of the
tables: 108, 121, 132 and 144""",

"""Feather Duster

Get through 10 rounds with
almost no dust damage""",

"""Hold Your Fire

Get through 10 rounds with
virtually all missiles finding
their target""",

"""Meteor Blaster

10 rounds with only a small
number of Meteors
getting past""",

"""Quick Shooter

Answer the questions to
recharge your energy at
express speed""",

"""Tacheon

Answer the questions to
recharge your energy
at the speed of light!""",

"""Meteors come from the sector just to the
right of The Moon. {} toggles pause/play
(you are now paused) {} skips to next round... but
Any escaping meteors reduce your health... but
Gold meteors are good - don't shoot them.
Avoid dust if possible, NB your craft is moving...
{} to shoot (costs psychic energy)
Later missiles will have strange gravity effects.
The number of missiles in flight at the same
time increases with the number of targets.
{}
""".format(*ALT_TEXT)]
########################################################################
class Medal(object):
  def __init__(self, shinesh, flatsh, reflimg, alpha, font, text, x, y,
                z, ry):
    self.achieved = False
    s = sin(radians(ry))
    c = cos(radians(ry))
    self.coin = pi3d.Model(file_string="models/coin.obj", x=x + R*s, y=y,
                                  z=z + R*c, sx=0.2, sy=0.2, sz=0.2, ry=ry)
    self.coin.set_draw_details(shinesh, [self.coin.buf[0].textures[0],
                              reflimg], 1.0, 0.7)
    self.coin.set_alpha(alpha)
    self.coin.set_material((0.5, 0.4, 0.0))
    
    self.string = pi3d.String(font=font, string=text, size=200.0,
                          x=x + R*0.5*s, y=y, z=z + R*0.5*c, ry=ry)
    self.string.set_shader(flatsh)

  def draw(self):
    self.coin.rotateIncY(0.15)
    self.coin.draw()
    self.string.draw()

  def achieve(self):
    self.achieved = True
    self.coin.set_alpha(1.0)

class Medals(object):
  def __init__(self, shinesh, flatsh, reflimg, font, x, y, z, free_version):
    self.free_version = free_version
    self.m_list = []
    for i in range(0, 7):
      self.m_list.append(Medal(shinesh, flatsh, reflimg, 0.35, font,
                        M_TEXT[i], x, y, z, i * 45))
    ry = 7 * 45
    s = sin(radians(ry))
    c = cos(radians(ry))
    self.summary = pi3d.String(font=font, string=M_TEXT[7], size=200.0,
                          x=x + R*0.5*s, y=y, z=z + R*0.5*c, ry=ry)
    self.summary.set_shader(flatsh)

  def draw(self):
    for m in self.m_list:
      m.draw()
    self.summary.draw()

  def q_check(self, questions, f_count):
    if self.free_version:
      return False
    new_medal = False
    #print(f_count)
    if f_count < TARGETS[0] and not self.m_list[5].achieved:
      self.m_list[5].achieve()
      new_medal = True
    if f_count < TARGETS[1] and not self.m_list[6].achieved:
      self.m_list[6].achieve()
      new_medal = True
    all_good = True
    for i in [0, 4, 11, 12, 15, 16, 24, 26, 28]:
      if questions[i].ratio > 0.2:
        all_good = False
        break
    if all_good and not self.m_list[0].achieved:
      self.m_list[0].achieve()
      new_medal = True
    all_good = True
    for i in [21, 32, 36, 38]:
      if questions[i].ratio > 0.2:
        all_good = False
        break
    if all_good and not self.m_list[1].achieved:
      self.m_list[1].achieve()
      new_medal = True
    return new_medal

  def s_check(self, last_ten, l_number):
    if self.free_version or len(last_ten) < 10:
      return False
    new_medal = False
    num = [0, 0, 0, 0, 0]
    for lt in last_ten:
      for i in range(5):
        num[i] += lt[i]
    ##### dust
    if num[0] < l_number * TARGETS[2] and not self.m_list[2].achieved:
      self.m_list[2].achieve()
      new_medal = True
    ##### missile hits
    if num[2] / num[1] > (TARGETS[3] - l_number * 0.0015) and not self.m_list[3].achieved:
      self.m_list[3].achieve()
      new_medal = True
    ##### meteor escapes
    if num[4] / num[3] < (TARGETS[4] + l_number * 0.002) and not self.m_list[4].achieved:
      self.m_list[4].achieve()
      new_medal = True
    return new_medal
