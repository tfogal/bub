#!python
# Library for reading FIN files, which are output from a mass
# spectrometer out at BU.  These are basically simple text files.
from __future__ import with_statement

class FIN:
  def __init__(self, filename):
    self._finfile = filename
    self._header = None
    self._date = None
    self._time_offset = None
    self._run_file = None

  def _read_header(self, openfile):
    openfile.readline().strip() # "title"
    self._date = openfile.readline().strip()
    self._run_file = openfile.readline().strip()
    for i in xrange(0, 4): openfile.readline()
    self._header = openfile.readline().strip().split(",")

  def set_time_offset(self, offset):
    '''The first column of all FIN files is a time specification.  However,
    FIN files come in groups; each file is when the spectrometer "starts over".
    Thus all the files will have the same times, but only the first file is
    correct; the times given in the second file actually start where the first
    file ended, and so on.  Thus we provide a way to increment the times this
    class returns to be "correct".'''
    self._time_offset = offset

  def element(self, element_name):
    '''Gets just the given field from the FIN file.  Raises IndexError if the
    element does not exist in the FIN file.  For this method, "Time" is
    considered an element.'''
    with open(self._finfile, "r") as fin:
      self._read_header(fin)

      # Yes, we could simply read every field and return out the one the user
      # wanted.  However the memory bound on this approach is the size of the
      # element they want plus the size of a line, as opposed to the file size.
      idex = 0
      try:
        idex = self._header.index(element_name)
      except ValueError:
        raise IndexError(element_name + " does not exist in " + self._finfile +
                         ".  Try one of " + " ".join(self._header))

      data = []
      if(element_name is "Time" and self._time_offset is not None):
        data = [float(x.strip().split(",")[idex])+self._time_offset
                for x in fin.readlines()]
      else:
        data = [float(x.strip().split(",")[idex]) for x in fin.readlines()]

      return data

  def date(self):
    """Returns the date of this FIN file's creation, as output by the scanner.
    This is assumed to be the second line of the FIN file."""
    if self._date is None:
      with open(self._finfile, "r") as ff:
        title = ff.readline().strip()
        self._date = ff.readline().strip()
        ff.close()
    return self._date

  def elements(self):
    """Returns a list of the elements stored in this FIN.  These are the keys
    which are used with self.element()!"""
    if self._header is None:
      # We haven't parsed the FIN file yet.  Parse just the header so we can
      # pull out the element names.
      with open(self._finfile, "r") as fin: self._read_header(fin)
    assert(self._header is not None)
    return self._header

  def run_filename(self):
    '''Third line of the FIN file.'''
    if self._run_file is None:
      with open(self._finfile, "r") as fin: self._read_header(fin)
    return self._run_file

if __name__ == "__main__":
  import datetime as dt
  import unittest

  class TestFIN(unittest.TestCase):

    def _write_simple(self, tofile):
      '''Writes a simple FIN file from some sample data I have.'''
      with open(tofile, "w") as fin:
        fin.write("Finnigan MAT ELEMENT Raw Data\n")
        fin.write(dt.datetime.now().strftime("%A, %B, %Y %H:%M:%S") + "\n")
        fin.write("101510lm2.FIN\n")
        fin.write("287\n0\n")
        fin.write("16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16\n")
        fin.write("CPS\n")
        self.elems = ["Time", "Li7", "Ca44", "Mn55", "Cu63", "Zn66", "Zn70",
                      "As75", "Se77", "Se82", "Rb85", "Mo95", "Ce140", "Au197",
                      "Pb207", "Pb208", "P31"]
        fin.write(",".join(self.elems) + "\n")
        d1 = [0.695000, 53733.500000, 5762171.500000, 723712.000000,
              6566.000000, 12124.500000, 29440.500000, 1262.000000,
              269480.000000, 41456.500000, 11366.500000, 631.000000,
              1641.000000, 252.000000, 505.000000, 1010.000000, 1069296.000000]
        fin.write(",".join([`d` for d in d1]) + "\n")
        d1 = [1.388000, 46771.500000, 6144815.000000, 752912.000000,
              5682.000000, 16420.500000, 32222.500000, 1514.500000,
              245692.000000, 38041.500000, 11240.000000, 757.000000,
              1010.000000, 252.500000, 631.000000, 1262.000000, 1506640.000000]
        fin.write(",".join([`d` for d in d1]) + "\n")
        fin.close()

    def setUp(self):
      self.testfile = ".testing.fin"
      self._write_simple(self.testfile)

    def tearDown(self):
      import os
      os.remove(self.testfile)

    def test_date(self):
      '''Ensure we read in the date hidden in the file.'''
      fin = FIN(self.testfile)
      self.assertEquals(fin.date(),
                        dt.datetime.now().strftime("%A, %B, %Y %H:%M:%S"))

    def test_parse(self):
      fin = FIN(self.testfile)
      # first column
      self.assertEqual(fin.element("Time"), [0.695, 1.388])
      self.assertEqual(fin.element("Li7"), [53733.5, 46771.5])
      # last column
      self.assertEqual(fin.element("P31"), [1069296.0, 1506640.0])

    def test_invalid_elem(self):
      fin = FIN(self.testfile)
      self.assertRaises(IndexError, fin.element, "JunkColumn")

    def test_offset(self):
      '''Make sure we properly apply time offsets.'''
      fin = FIN(self.testfile)
      offset = 198.880997
      fin.set_time_offset(offset)
      lst = [x + offset for x in [0.695, 1.388]]
      self.assertEqual(fin.element("Time"), lst)
      # make sure we don't add the offset to other fields
      self.assertEqual(fin.element("P31"), [1069296.0, 1506640.0])

    def test_elements(self):
      fin = FIN(self.testfile)
      fin_elems = fin.elements()
      for i in xrange(0, len(self.elems)):
        self.assertEqual(self.elems[i], fin_elems[i])

  unittest.main()
