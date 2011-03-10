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
import math
import os

import fin

def validate(): return os.getenv("BUB_NO_VALIDATE") is None
def equalf(a,b): EPSILON=1E-2; return math.fabs(a-b) < EPSILON

class FINDir:
  def __init__(self, directory, pattern):
    '''Initializes a FIN directory.  The 'directory' parameter should be a
    path, and 'pattern' should be a glob string which matches the set of FIN
    files you care about.'''
    self._directory = directory
    self._pattern = pattern
    self._date = None
    self._elements = None
    self._runfilename = None
    self._scan_time = None # time to scan one line
    self._points_per_file = None

  def _files(self):
    files = glob.glob(self._directory + os.sep + self._pattern)
    files.sort()
    return files

  def element(self, element_name):
      '''Gets the full data for the given element, by parsing every FIN file in
      the directory.  This will take some time!'''
      data = []
      last_time = 0.0
      for f in self._files():
        ff = fin.FIN(f)
        ff.set_time_offset(last_time)

        # Cache some metadata clients sometimes want to query.
        if self._elements is None: self._elements = ff.elements()
        if self._runfilename is None: self._runfilename = ff.run_filename()
        if self._scan_time is None: self._scan_time = ff.time()

        # All the run filenames should be the same... else the user is mixing
        # data from different data sets.
        if validate() and self._runfilename != ff.run_filename():
          raise UserWarning("I saw a 'run filename' (3rd line of a FIN file) "
                            "of " + self._runfilename + ", but I'm looking at "
                            + f + " right now, and it has a run filename of "
                            + ff.run_filename() + ".  This probably means you "
                            "are mixing FIN files from logically separate "
                            "data sets.\n"
                            "You can set the environment variable "
                            "'BUB_NO_VALIDATE' to get around this, but you're "
                            "probably processing unassociated data together, "
                            "which does not make sense.")
        if validate() and not equalf(self._scan_time, ff.time()):
          raise UserWarning("Scan times are changing.")

        elem = ff.element(element_name)
        if element_name is "Time": last_time = max(elem)
        if self._points_per_file is None: self._points_per_file = len(elem)
        if validate() and self._points_per_file != len(elem):
          raise UserWarning("Points per file changing.")
        data.extend(elem)

      return data

  def date(self):
    '''Returns the date in the first FIN file.'''
    if self._date is None:
      # User hasn't called 'element' yet; we need to parse it =(
      ff = fin.FIN(self._files()[0])
      self._date = ff.date()
    assert(self._date is not None)
    return self._date

  def time_per_scanline(self):
    if self._scan_time is None:
      self.element("Time") # could be anything, we just need to read data.
    return self._scan_time

  def elements(self):
    '''Returns the list of elements in this data set.'''
    if self._elements is None:
      ff = fin.FIN(self._files()[0])
      self._elements = ff.elements()
    return self._elements

  def run_filename(self):
    '''The "run filename" is the 3rd line of the FIN files.  For a single run
    (i.e. all the associated files in a FINDir), all the run filenames should
    be the same.'''
    if self._runfilename is None:
      ff = fin.FIN(self._files()[0])
      self._runfilename = ff.run_filename()
    return self._runfilename

  def scanning_time_per_line(self):
    if self._scan_time is None:
      ff = fin.FIN(self._files()[0])
      self._scan_time = ff.time()
    return self._scan_time

  def _data_points_per_line(self):
    if self._points_per_file is None:
      ff = fin.FIN(self._files()[0])
      # we know "Time" will always exist.
      self._points_per_file = len(ff.element("Time"))
    return self._points_per_file

  def _n_files(self): return len(self._files())

  def x(self): return self._data_points_per_line()
  def y(self): return self._n_files()

if __name__ == "__main__":
  import unittest

  class TestFINDir(unittest.TestCase):
    '''There's a significant issue with testing this: the user needs a
    directory full of FIN files.  I've hardcoded a directory I have in here for
    now, unfortunately.  Sorry...'''

    def setUp(self):
      test1 = os.sep.join([os.getenv("HOME"), "data",
                           "bu-biometallomics", "BottomLeft",
                           "TOPLEFTFIN2"])
      test2 = os.sep.join([os.getenv("HOME"), "data", "bu-biometallomics",
                           "new-data", "fins"])
      self._fd = FINDir(test1, "ABC*FIN2")

    def test_element_entries(self):
      self.assertEqual(len(self._fd.element("Li7")), 22099)

    def test_element_time_increasing(self):
      '''Time should monotonically increase.'''
      t = self._fd.element("Time")
      for i in xrange(1, len(t)): self.assertTrue(t[i-1] < t[i])

    def test_invalid_element(self):
      '''Invalid element names should throw an exception.'''
      self.assertRaises(IndexError, self._fd.element, "ThisIsGarbage!")

    def test_date(self):
      self.assertEqual(self._fd.date(), "Friday, October 15, 2010 21:49:14")

    def test_elements(self):
      '''Test explicit elements query.'''
      el = ["Time", "Li7", "Ca44", "Mn55", "Cu63", "Zn66", "Zn70", "As75",
            "Se77", "Se82", "Rb85", "Mo95", "Ce140", "Au197", "Pb207", "Pb208",
            "P31"]
      self.assertEqual(len(self._fd.elements()), len(el))
      for i in xrange(0, len(el)):
        self.assertEqual(self._fd.elements()[i], el[i])

    def test_elements_data(self):
      '''Test reading the elements while reading data.'''
      el = ["Time", "Li7", "Ca44", "Mn55", "Cu63", "Zn66", "Zn70", "As75",
            "Se77", "Se82", "Rb85", "Mo95", "Ce140", "Au197", "Pb207", "Pb208",
            "P31"]
      self.assertEqual(len(self._fd.element("Rb85")), 22099)
      self.assertEqual(len(self._fd.elements()), len(el))
      for i in xrange(0, len(el)):
        self.assertEqual(self._fd.elements()[i], el[i])

    def test_runfilename(self):
      self.assertEqual(self._fd.run_filename(), "101510lm2.FIN")

    def test_scan_time(self):
      self.assert_(equalf(self._fd.scanning_time_per_line(), 198.185997))

    def test_data_points(self):
      self.assertEqual(self._fd._data_points_per_line(), 287)

    def test_n_files(self):
      self.assertEqual(self._fd._n_files(), 77)

    def text_xy(self):
      self.assertEqual(self._fd.x(), 287)
      self.assertEqual(self._fd.y(), 77)

  unittest.main()
