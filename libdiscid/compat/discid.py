# -*- coding: utf-8 -*-

# Copyright 2013 Sebastian Ramacher <sebastian+dev@ramacher.at>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

""" python-discid compat layer

This module provides a compatible layer so that python-libdiscid can be used as
a replacement for python-discid. It provides an interface compatible with
python-discid version 1.0.2.

>>> try:
>>>   from libdiscid.compat.discid
>>> except ImportError:
>>>   import discid
"""

from __future__ import division

import libdiscid
import libdiscid.discid
import operator

_INVERSE_FEATURES= {
    libdiscid.FEATURES_MAPPING[libdiscid.FEATURE_READ]: libdiscid.FEATURE_READ,
    libdiscid.FEATURES_MAPPING[libdiscid.FEATURE_MCN]: libdiscid.FEATURE_MCN,
    libdiscid.FEATURES_MAPPING[libdiscid.FEATURE_ISRC]: libdiscid.FEATURE_ISRC
  }

class _NoneHelper(object):
  def __getattr__(self, name):
    if name in ('id', 'freedb_id', 'submission_url', 'first_track',
                'last_track', 'sectors', 'mcn'):
      return None

    return super(NoneHelper, self).__getattr__(name)

def _sectors_to_seconds(sectors):
  SECTORS_PER_SECOND = 75
  remainder = sectors % SECTORS_PER_SECOND
  return sectors // SECTORS_PER_SECOND + \
    (1 if remainder > SECTORS_PER_SECOND // 2 else 0)

# exceptions defined in discid
DiscError = libdiscid.discid.DiscError

class TOCError(Exception):
  pass

# classes defined in discid
class Track(object):
  def __init__(self, disc, number):
    self.disc = disc
    self.number = number

  def __str__(self):
    return str(self.number)

  @property
  def offset(self):
    return self.disc.track_offsets[self.number - self.disc.first_track]

  @property
  def sectors(self):
    return self.disc.track_lengths[self.number - self.disc.first_track]
  length = sectors

  @property
  def seconds(self):
    return _sectors_to_seconds(self.sectors)

  @property
  def isrc(self):
    try:
      value = self.disc.track_isrcs[self.number - self.disc.first_track]
    except NotImplementedError:
      return None
    return value if value != '' else None

class Disc(object):
  def __init__(self):
    self.disc = _NoneHelper()
    self.tracks = []

  def read(self, device, features=[]):
    self.disc = libdiscid.read(device, reduce(
      operator.or_, (_INVERSE_FEATURES[feature] for feature in FEATURES), 0))
    self.tracks = [
      Track(self.disc, numb) for numb in xrange(self.disc.first_track,
                                                self.disc.last_track + 1)]
    return True

  def put(self, first, last, disc_sectors, track_offsets):
    try:
      self.disc = libdiscid.put(first, last, disc_sectors, track_offsets)
    except DiscError as disc_error:
      raise TOCError(str(disc_error))

    self.tracks = [
      Track(self.disc, num) for num in xrange(self.disc.first_track,
                                              self.disc.last_track + 1)]
    return True

  @property
  def id(self):
    return self.disc.id

  @property
  def freedb_id(self):
    return self.disc.freedb_id

  @property
  def submission_url(self):
    return self.disc.submission_url

  @property
  def first_track_num(self):
    return self.disc.first_track

  @property
  def last_track_num(self):
    return self.disc.last_track

  @property
  def sectors(self):
    return self.disc.sectors
  length = sectors

  @property
  def seconds(self):
    return _sectors_to_seconds(self.sectors) if self.sectors is not None \
      else None

  @property
  def mcn(self):
    try:
      value = self.disc.mcn
    except NotImplementedError:
      return None
    return value if value != '' else None

# functions defined in discid
get_default_device = libdiscid.default_device

def read(device=None, features=[]):
  disc = Disc()
  disc.read(device, features)
  return disc

def put(first, last, disc_sectors, track_offsets):
  disc = Disc()
  disc.put(first, last, disc_sectors, track_offsets)
  return disc

# constants defined in discid
__version__ = '1.0.2 (compat wrapper from python-discid %s)' % \
  (libdiscid.__version__, )
""" This is the version of python-discid this layer is compatible with. """

LIBDISCID_VERSION_STRING = libdiscid.__discid_version__
FEATURES = libdiscid.FEATURES
FEATURES_IMPLEMENTED = (libdiscid.FEATURE_READ, libdiscid.FEATURE_MCN,
                        libdiscid.FEATURE_ISRC)