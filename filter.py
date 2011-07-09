#!python
class Filter:
  def __init__(self):
    self._parameters = {}

  def set_parameter(self, key, value, minval=None,maxval=None):
    self._parameters[key] = value
    if minval != None and maxval != None:
      self._parameters[key] = [value, (minval,maxval)]

  def get_parameter(self, key):
    if type(key) == list: # we just want the value in that case.
      return self._parameters[key][0]
    return self._parameters[key]

  def get_all_parameters(self):
    return self._parameters
