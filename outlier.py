#!python
import math
from filter import Filter

def avg(l): return math.fsum(l) / len(l)

class Outlier(Filter):
  '''This filter removes outliers within a data set.'''
  def __init__(self):
    Filter.__init__(self)
    self._input = None
    self._dimensions = None
    self._output = None
    # cutoff: we compare the neighborhood average to the current datum; if the
    # datum is in the 95th (or higher) percentile, it is considered an outlier.
    self.set_parameter("cutoff", 0.95, 0.0,1.0)

  def set_input(self, raw_data, dims):
    self._dimensions = dims
    self._input = raw_data

  def get_output(self):
    if self._output == None:
      self.execute()
    return self._output

  def _is_outlier(self, stencil):
    '''Identifies if a particular datum is an outlier.  Expects to get the datum
       as well as neighborhood information.  We expect to receive a 9-point
       stencil, with the datum at index [4].'''
    assert(len(stencil) == 9)
    total = math.fsum(stencil[0:4] + stencil[5:9])
    avg = total / 9.0
    diff = math.fabs(stencil[4] - avg)
    print "param:", self.get_parameter("cutoff")
    cutoff = self.get_parameter("cutoff") * avg
    if diff > cutoff: return True
    return False

  def _average_out_outliers(self, data, dimensions):
    minimum = min(data)
    out = []
    for y in xrange(1, dimensions[1]-1):
      for x in xrange(1, dimensions[0]-1):
        idx1 = (y-1)*dimensions[0] + x-1 # line above
        idx2 = (y-0)*dimensions[0] + x-1
        idx3 = (y+1)*dimensions[0] + x-1 # line below
        stencil = data[idx1:idx1+3] + data[idx2:idx2+3] + data[idx3:idx3+3]
        if self._is_outlier(stencil):
          out[idx2+1] = avg(data[idx1:idx1+3] + [data[idx2]] + [data[idx2+2]] +
                            data[idx3:idx3+3])
    assert(len(out) == len(data))
    return out

  def execute(self):
    assert(self._dimensions != None)

    self._output = self._average_out_outliers(self._input, self._dimensions)
    # we don't need the input anymore.
    del self._input
    self._input = None
