#!python
import copy
import math
from filter import Filter

def avg(l): return math.fsum(l) / len(l)

class Outlier(Filter):
  '''This filter removes outliers within a data set.'''
  def __init__(self):
    Filter.__init__(self)
    self._name = "Outlier"
    self._input = None
    self._dimensions = None
    self._output = None
    # cutoff: we compare the neighborhood average to the current datum; if the
    # datum is in the 95th (or higher) percentile, it is considered an outlier.
    self.set_parameter_floatrange("cutoff", 0.95, 0.0,1.0)
    # if the averaging out is inclusive of the datum in question
    self.set_parameter("inclusive", False, bool)

  def set_input(self, raw_data, dims):
    self._dimensions = dims
    self._input = raw_data

  def get_output(self):
    if self._output == None:
      self.execute()
    return self._output

  def _is_outlier(self, value, stencil):
    '''Identifies if a particular datum is an outlier.  Expects to get the datum
       as well as neighborhood information.'''
    total = math.fsum(stencil)
    avg = total / len(stencil)
    diff = math.fabs(value - avg)
    cutoff = self.get_parameter("cutoff") * avg
    if diff > cutoff: return True
    return False

  def _index(self, x, y):
    '''Gives the 1D index from the 2D index.'''
    return y * self._dimensions[0] + x

  def _average_out_outliers(self, data, dimensions):
    out = copy.deepcopy(data)
    for y in xrange(1, dimensions[1]-1):
      for x in xrange(1, dimensions[0]-1):
        idx1 = (y-1)*dimensions[0] + x-1 # line above
        idx2 = (y-0)*dimensions[0] + x-1
        idx3 = (y+1)*dimensions[0] + x-1 # line below
        stencil = out[idx1:idx1+3] + out[idx2:idx2+3] + out[idx3:idx3+3]
        out[idx2+1] = data[idx2+1]  # copy the datum at first...
        if self._is_outlier(data[self._index(x,y)], stencil):
          # replace it with the average if it's an outlier.
          if self.get_parameter("inclusive"):
            out[idx2+1] = avg(stencil)
          else:
            out[idx2+1] = avg(out[idx1:idx1+3] + [out[idx2]] +
                              [out[idx2+2]] + out[idx3:idx3+3])

    # get the 4 corners.
    idx = self._index # to keep it short.
    x,y = 0,0 # top left
    stencil = out[idx(x,y):idx(x,y)+2] + out[idx(x,y+1):idx(x,y+1)+2]
    if self._is_outlier(data[idx(x,y)], stencil): out[idx(x,y)] = avg(stencil)

    x,y = dimensions[0]-1,0 # top right
    stencil = out[idx(x-2,y):idx(x,y)] + out[idx(x-2,y+1):idx(x,y+1)]
    if self._is_outlier(data[idx(x,y)], stencil): out[idx(x,y)] = avg(stencil)

    x,y = 0,dimensions[1]-1 # bottom left
    stencil = out[idx(x,y-1):idx(x+2,y-1)] + out[idx(x,y):idx(x+2,y)]
    if self._is_outlier(data[idx(x,y)], stencil): out[idx(x,y)] = avg(stencil)

    x,y = dimensions[0]-1,dimensions[1]-1 # bottom right
    stencil = out[idx(x-2,y-1):idx(x,y-1)] + out[idx(x-2,y):idx(x,y)]
    if self._is_outlier(data[idx(x,y)], stencil): out[idx(x,y)] = avg(stencil)

    assert(len(out) == len(data))
    return out

  def execute(self):
    assert(self._dimensions != None)

    self._output = self._average_out_outliers(self._input, self._dimensions)
    # we don't need the input anymore.
    del self._input
    self._input = None
