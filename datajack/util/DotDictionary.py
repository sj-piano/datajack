#!/usr/bin/python




def main():
  # Create blank DotDict.
  d1 = DotDict()
  d1.a = 'hello'
  d1.b = 'world'
  print d1.a
  print d1['b']
  # Make a DocDict from a dict.
  d2 = {'foo': 1, 'bar': 123123, 'baz': '5000'}
  d3 = DotDict(d2)
  print 'd3:', d3
  print 'd3.foo:', d3.foo
  print "d3['foo']:", d3['foo']
  # Make a DocDict from a nested dict.
  d4 = {'foo': 1, 'bar': {'jupiter': 5, 'mars': 123975}, 'baz': 5000}
  d5 = DotDict(d4)
  print 'd5:', d5
  print 'd5.foo:', d5.foo
  print 'd5.bar.jupiter:', d5.bar.jupiter




class DotDict(dict):
  """dot.notation access to dictionary attributes"""

  def __init__(self, dictionary=None):
    if dictionary is None:
      return
    if not isinstance(dictionary, dict):
      raise TypeError()
    self.importDict(dictionary)


  def importDict(self, d):
    for k, v in d.items():
      if isinstance(v, dict):
        self[k] = DotDict(v) # recurse for nested dictionaries.
      else:
        self[k] = v


  def __getattr__(self, key):
    try:
      return self[key]
    except KeyError:
      raise AttributeError(key)


  def __setattr__(self, key, value):
    self[key] = value




if __name__ == '__main__':
  main()
