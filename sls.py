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
def validate(): return os.getenv("BUB_NO_VALIDATE") is None

class SLS:
  def __init__(self, filename):
    self._sls = filename
    self._start = (None, None, None)
    self._stop = (None, None, None)
    self._energy = None
    self._repetition = None
    self._spot_size = None

  def start(self):
    if self._start[0] is None: self._parse()
    return self._start

  def stop(self):
    if self._stop[0] is None: self._parse()
    return self._stop

  def energy(self):
    if self._energy is None: self._parse()
    return self._energy

  def spot_size(self):
    if self._spot_size is None: self._parse()
    return self._spot_size

  class IncompleteGroup: pass

  def _read_group(self, sls):
    """Reads one of those groups of 8.  Returns a dict with keys of 'start',
       'stop', 'energy', 'repetition' and 'spot_size'"""
    try:
      start = (float(sls.readline().strip()),
               float(sls.readline().strip()),
               float(sls.readline().strip()))
      stop = (float(sls.readline().strip()),
              float(sls.readline().strip()),
              start[2]) # we aren't really given a Z stop ever, at present.
      energy = float(sls.readline().strip())
      repetition = float(sls.readline().strip())
      spot_size = float(sls.readline().strip())
      return {'start': start, 'stop': stop, 'energy': energy,
              'repetition': repetition, 'spot_size': spot_size}
    except ValueError:
      # we'll hit this if there's not enough lines for a full record.
      raise self.IncompleteGroup

  def _uninitialized(self):
    """Lets us know we've never initialized internal data members (i.e. we
       have not yet read anything)."""
    # To be correct, we should probably check all members, but we rely on them
    # all getting set together at present.
    return self._energy is None

  def _parse(self):
    with open(self._sls, "r") as sls:

      while sls:
        location = sls.tell()
        # "line" is a line from the scanner, not a line from the file.
        line = None
        try:
          # Our basic approach here is to read sets of values (8 lines) which
          # are associated (all come from a single scan line) until hit the
          # end.  Then we'll back up and read what we're looking for.
          line = self._read_group(sls)
          if self._uninitialized():
            self._start = line['start']
            self._stop = line['stop']
            self._energy = line['energy']
            self._repetition = line['repetition']
            self._spot_size = line['spot_size']
          self._start = (min(self._start[0], line['start'][0]),
                         min(self._start[1], line['start'][1]),
                         min(self._start[2], line['start'][2]))
          self._stop = (max(self._stop[0], line['stop'][0]),
                        max(self._stop[1], line['stop'][1]),
                        max(self._stop[2], line['stop'][2]))
          if validate() and self._energy != line['energy']:
            raise UserWarning("Energy rate changed while scanning.  Very odd.")
          if validate() and self._repetition != line['repetition']:
            raise UserWarning("Repetition rate changed while scanning.  Odd.")
          if validate() and self._spot_size != line['spot_size']:
            raise UserWarning("Spot size changed while scanning.  VERY BAD. " +
                              " This data is likely to be completely invalid."+
                              "  You should run another experiment.")
        except self.IncompleteGroup:
          break
          sls.seek(location)
          if(sls):
            scan_rate = int(sls.readline().strip())
            times = int(sls.readline().strip())
            delay = int(sls.readline().strip())
            gas_blank = float(sls.readline().strip())
            delfocus = float(sls.readline().strip())
            sls.seek(0, os.SEEK_END)
            sls.readline()

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
                14004.0, -8569.0, -3306, 14004.0, 100, 20, 25,
                25, 1, 12, 0, 1.25, 1)
      with open(self._testfile, "w") as sls:
        for v in values: sls.write(`v` + "\n")

    def tearDown(self):
      os.remove(self._testfile)

    def test_sanity(self):
      s = SLS(self._testfile)
      s._parse()

    def test_start(self):
      s = SLS(self._testfile)
      self.assertEqual(s.start(), (-10607, 14004, -8569))

    def test_stop(self):
      s = SLS(self._testfile)
      self.assertEqual(s.stop(), (-3306, 14254, -8569))

    def test_bounds(self):
      s = SLS(self._testfile)
      self.assert_(s.start()[0] < s.stop()[0])
      self.assert_(s.start()[1] < s.stop()[1])
      self.assert_(s.start()[2] <= s.stop()[2]) # 2D data, right now.

    def test_energy(self):
      s = SLS(self._testfile)
      self.assertEqual(s.energy(), 100)

    def test_spot_size(self):
      s = SLS(self._testfile)
      self.assertEqual(s.spot_size(), 25)

    def test_nothing(self): pass

  unittest.main()
