#!python
# Library for reading SLS files.
#
# SLS files come from the apparatus that gathers and stores the data from the
# mass spectrometer.  It basically looks like a text file with a bunch of
# numbers, one per line.
# A lot of the information appears to be useless, or at least of unknown value,
# but the one important bit we can grab from these files is the dimension of
# the data.
from __future__ import with_statement
import os

# should we validate what we're seeing in the files?
#def validate(): return os.getenv("BUB_NO_VALIDATE") is None
# hack for now... seems the information I have on what values are fixed
# is not valid?
def validate(): return False

class SLS:
  def __init__(self, filename):
    self._sls = filename
    self._start = (None, None)
    self._zpos = None
    self._stop = (None, None)
    self._energy = None
    self._repetition = None
    self._spot_size = None
    self._line_separation = None

  def start(self):
    if self._start[0] is None: self._parse()
    return self._start

  def z_position(self):
    if self._zpos is None: self._parse()
    return self._zpos

  def stop(self):
    if self._stop[0] is None: self._parse()
    return self._stop

  def energy(self):
    if self._energy is None: self._parse()
    return self._energy

  def spot_size(self):
    if self._spot_size is None: self._parse()
    return self._spot_size

  def line_separation(self):
    if self._line_separation is None: self._parse()
    return self._line_separation

  def _parse(self):
    with open(self._sls, "r") as sls:
      self._start = (float(sls.readline().strip()),
                     float(sls.readline().strip()))
      self._zpos = float(sls.readline().strip())
      self._stop = (float(sls.readline().strip()),
                    float(sls.readline().strip()))
      self._energy = float(sls.readline().strip())
      self._repetition = float(sls.readline().strip())
      self._spot_size = float(sls.readline().strip())
      self._line_separation = float(sls.readline().strip())
      sls.readline().strip() # 'Line number'?

      def read_and_validate_int(value):
        i = int(float(sls.readline().strip()))
        if i != value and validate():
          raise UserWarning("Fixed value should be " + `value` + " but it is " +
                            `i` + " instead!")
      read_and_validate_int(-10765)
      read_and_validate_int(-4953)
      sls.readline() # unknown what this line means.
      read_and_validate_int(100)
      read_and_validate_int(20)
      read_and_validate_int(10)

if __name__ == "__main__":
  import unittest

  class TestSLS(unittest.TestCase):
    def setUp(self):
      self._testfile = ".testing.sls"
      values = (-10607, 14254, -8569, -3306, 14254, 100, 20, 25, -10607.0,
                14204.0, -8569.0, -3306, 14204.0, 100, 20, 25, -10607.0,
                14154.0, -8569.0, -3306, 14154.0, 100, 20, 25, -10607.0,
                14104.0, -8569.0, -3306, 14104.0, 100, 20, 25, -10607.0,
                14054.0, -8569.0, -3306, 14054.0, 100, 20, 25, -10607.0,
                14004.0, -8569.0, -3306, 14004.0)
      with open(self._testfile, "w") as sls:
        for v in values: sls.write(`v` + "\n")

    def tearDown(self):
      os.remove(self._testfile)

    def test_sanity(self):
      s = SLS(self._testfile)
      s._parse()

    def test_start(self):
      s = SLS(self._testfile)
      self.assertEqual(s.start(), (-10607, 14254))

    def test_zpos(self):
      s = SLS(self._testfile)
      self.assertEqual(s.z_position(), -8569)

    def test_stop(self):
      s = SLS(self._testfile)
      self.assertEqual(s.stop(), (-3306, 14254))

    def test_energy(self):
      s = SLS(self._testfile)
      self.assertEqual(s.energy(), 100)

    def test_spot_size(self):
      s = SLS(self._testfile)
      self.assertEqual(s.spot_size(), 25)

    def test_line_separation(self):
      s = SLS(self._testfile)
      self.assertEqual(s.line_separation(), -10607.0)

    def test_nothing(self): pass

  unittest.main()
