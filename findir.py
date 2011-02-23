#!python
# Library for reading *sets* of FIN files.
#
# We normally get a whole directory of these things.  Each file is part of the
# data; one should arrange the files linearly (they all have file numbers) to
# form the full dataset.
# To make matters more difficult, the first column (Time) is special.  See,
# each of these files comes from a single scan with the mass spectrometer, and
# the spectrometer has no idea it's doing multiple passes.  Thus the "Time"
# code specification in each file starts at 0... even though the second file in
# the sequence really starts off where the first file left off.  Argh.  We
# handle this by figuring out the max time code, and using our FIN() classes'
# set_time_offset method to get the appropriate time code.
import glob
import os

import fin

class FINDir:
  def __init__(self, directory, pattern):
    '''Initializes a FIN directory.  The 'directory' parameter should be a
    path, and 'pattern' should be a glob string which matches the set of FIN
    files you care about.'''
    self._directory = directory
    self._pattern = pattern

  def element(self, element_name):
      '''Gets the full data for the given element, by parsing every FIN file in
      the directory.  This will take some time!'''
      data = []
      last_time = 0.0
      for f in glob.iglob(self._directory + os.sep + self._pattern):
        ff = fin.FIN(f)
        ff.set_time_offset(last_time)

        elem = ff.element(element_name)
        if element_name is "Time": last_time = max(elem)
        data.extend(elem)

      return data

if __name__ == "__main__":
  import unittest

  class TestFINDir(unittest.TestCase):
    def test_element_entries(self):
      fd = FINDir(os.sep.join([os.getenv("HOME"), "data", "bu-biometallomics",
                              "BottomLeft", "TOPLEFTFIN2"]), "ABC*FIN2")
      self.assertEqual(len(fd.element("Li7")), 22099)

    def test_element_time_increasing(self):
      '''Time should monotonically increase.'''
      fd = FINDir(os.sep.join([os.getenv("HOME"), "data", "bu-biometallomics",
                              "BottomLeft", "TOPLEFTFIN2"]), "ABC*FIN2")
      t = fd.element("Time")
      for i in xrange(1, len(t)): self.assertTrue(t[i-1] < t[i])

    def test_invalid_element(self):
      '''Invalid element names should throw an exception.'''
      fd = FINDir(os.sep.join([os.getenv("HOME"), "data", "bu-biometallomics",
                              "BottomLeft", "TOPLEFTFIN2"]), "ABC*FIN2")
      self.assertRaises(IndexError, fd.element, "ThisIsGarbage!")

  unittest.main()
