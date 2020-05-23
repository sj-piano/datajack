from operator import itemgetter
import inspect




def confirmNoArgs(args):
	callerName = inspect.stack()[1][3]
	if not isinstance(args, tuple):
		raise TypeError
	if args != ():
		raise ValueError("Function/method '{c}' doesn't accept positional args.".format(c=callerName))




def getRequiredKeys(dictionary, requiredStr):
	# Example requiredStr: 'data:s, logger'
	if not isinstance(dictionary, dict):
		raise TypeError
	if not isinstance(requiredStr, str):
		raise TypeError
	required = requiredStr.split(', ')
	results = []
	types = {'i': int, 's': str}
	for item in required:
		if ':' in item:
			key, valueTypeChar = item.split(':')
			valueType = types[valueTypeChar]
		else:
			key = item
			valueType = None
		if not key in dictionary:
			raise KeyError("Did not find required key: {k}".format(k=key))
		value = dictionary[key]
		if valueType is not None:
			if not isinstance(value, valueType):
				msg = "Dictionary item '{k}' is not a '{t}', as was specified. Instead, it is a '{t2}'.".format(k=key, t=valueType.__name__, t2=type(value).__name__)
				raise TypeError(msg)
		results.append(value)
	if len(results) == 1:
		return results[0]
	return results




def getOptionalKeys(dictionary, optionalStr, defaults):
	# Example optionalStr: 'parent, line:i, lineIndex:i'
	if not isinstance(dictionary, dict):
		raise TypeError
	if not isinstance(optionalStr, str):
		raise TypeError
	if not isinstance(defaults, tuple):
		raise TypeError
	optional = optionalStr.split(', ')
	results = []
	types = {'i': int, 's': str}
	for i, item in enumerate(optional):
		default = defaults[i]
		if ':' in item:
			key, valueTypeChar = item.split(':')
			valueType = types[valueTypeChar]
		else:
			key = item
			valueType = None
		if key in dictionary:
			value = dictionary[key]
		else:
			value = default
		if valueType is not None:
			if not isinstance(value, valueType):
				msg = "Optional dictionary item '{k}' found but is not a '{t}', as was specified. Instead, it is a '{t2}'.".format(k=key, t=valueType.__name__, t2=type(value).__name__)
				raise TypeError(msg)
		results.append(default)
	if len(results) == 1:
		return results[0]
	return results




def stop(msg=None):
	if msg: print "\n%s\n"%msg
	import sys; sys.exit()
