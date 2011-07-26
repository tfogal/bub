#!python

class Filter:
  '''A filter on some data.  Filters must define 'set_input', 'get_output', and
     'execute' operations.  This base class only handles parameters for the
     underlying filter.'''
  def __init__(self):
    self._parameters = {}

  def set_parameter(self, key, value, ptype):
    self._parameters[key] = [value, ptype]

  # convenience method to not specify the type
  def set_parameter_floatrange(self, key, value, minval,maxval):
    self._parameters[key] = [value, float]
    if minval != None and maxval != None:
      self._parameters[key] = [value, float, (minval,maxval)]

  def get_parameter(self, key):
    return self._parameters[key][0]

  def get_all_parameters(self):
    return self._parameters
