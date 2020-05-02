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
	
	# https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary
	# https://github.com/fabric/fabric/blob/1.13.1/fabric/utils.py#L186
	
	def __init__(self, d=None): # d = dictionary
		if not d:
			pass
		elif isinstance(d, dict):
			d2 = self.dictToDotDict(d)
			for k, v in d2.items():
				self[k] = v
		else:
			raise TypeError("If an argument is passed to init function, it must be a dict.")
	
	def dictToDotDict(self, d):
		newD = DotDict()
		for k, v in d.items():
			if isinstance(v, dict):
				newD[k] = self.dictToDotDict(v) # recurse for nested dictionaries.
			else:
				newD[k] = v
		return newD

	def __getattr__(self, key):
		try:
			return self[key]
		except KeyError:
			raise AttributeError(key)
	
	def __setattr__(self, key, value):
		self[key] = value




if __name__ == '__main__':
	main()
