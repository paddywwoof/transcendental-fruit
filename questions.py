#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

import demo
import pi3d
import random

class Question(object):
  right = 0
  wrong = 0
  ratio = 1.0
  invop = {'x':'/', '+':'-'} # dict to return inverse of operation

  def __init__(self, val1, val2, op='x'):
    self.op = op if op == 'x' else '+'
    self.vals = [val1, val2]

  def make_qanda(self):
    ''' returns a string question and integer answer
    '''
    ans = self.vals[0] * self.vals[1] if self.op == 'x' else self.vals[0] + self.vals[1]
    (i, j) = (0, 1) if random.random() > 0.5 else (1, 0)
    if random.random() > 0.5:
      question = '{} {} {} ='.format(self.vals[i], self.op, self.vals[j])
    else:
      question = '{} {} {} ='.format(ans, self.invop[self.op], self.vals[i])
      ans = self.vals[j]
    return question, ans

questions = [Question(7,8), Question(3,4), Question(4,6,'+'), Question(3,6),
             Question(4,7), Question(12,2), Question(5,5,'+'), Question(4,9),
             Question(2,2), Question(3,7,'+'), Question(6,6), Question(6,9),
             Question(3,7), Question(2,5,'+'), Question(4,8), Question(6,12),
             Question(2,3), Question(8,8), Question(3,5,'+'), Question(8,12),
             Question(3,6,'+'),Question(11,11), Question(3,3), Question(4,6),
             Question(6,7), Question(3,12), Question(7,7), Question(3,8),
             Question(7,12), Question(4,4), Question(9,9), Question(6,8),
             Question(2,8,'+'),Question(7,9), Question(2,9), Question(4,12),
             Question(2,4),Question(2,6), Question(3,9), Question(8,9),
             Question(11,12), Question(2,4,'+'), Question(2,8), Question(5,7),
             Question(9,12), Question(2,7), Question(12,12), Question(5,9)]
'''
##### this bit to generate the images as a one-off #####################
from PIL import Image, ImageDraw, ImageFont

n_tex = {}
imgfont = ImageFont.truetype('data/FreeSans.ttf', 48)

for q in questions:
  nlist = [q.vals[0], q.vals[1], q.vals[0] * q.vals[1] if q.op == '*' else q.vals[0] + q.vals[1]]
  for n in nlist:
    if not (n in n_tex):
      n_tex[n] = '={}'.format(n) # pi3d.FixedString('data/FreeSans.ttf', '={}'.format(n))
      im = Image.new("RGB", (128, 128), (255, 255, 255, 255))
      draw = ImageDraw.Draw(im)
      width, height = imgfont.getsize(n_tex[n])
      draw.text(((128.0 - width) / 2.0, (128.0 - height) / 2.0), n_tex[n], font=imgfont, fill=(0, 0, 0, 255))
      im.save('data/{}.jpg'.format(n))
'''

