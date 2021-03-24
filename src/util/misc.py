from operator import itemgetter
import inspect




def confirm_no_args(args):
  caller_name = inspect.stack()[1][3]
  if not isinstance(args, tuple):
    raise TypeError
  if args != ():
    raise ValueError("Function/method '{c}' doesn't accept positional args.".format(c=caller_name))




def get_required_items(dictionary, required_str):
  # Example required_str: 'data:s, logger'
  if not isinstance(dictionary, dict):
    raise TypeError
  if not isinstance(required_str, str):
    raise TypeError
  required_items = required_str.split(', ')
  results = []
  types = {'i': int, 's': str}
  for item in required_items:
    if ':' in item:
      key, value_type_char = item.split(':')
      value_type = types[value_type_char]
    else:
      key = item
      value_type = None
    if not key in dictionary:
      raise KeyError("Did not find required key: {k}".format(k=key))
    value = dictionary[key]
    if value_type is not None:
      if not isinstance(value, value_type):
        msg = "Dictionary item '{k}' is not a '{t}', as was specified. Instead, it is a '{t2}'.".format(k=key, t=value_type.__name__, t2=type(value).__name__)
        raise TypeError(msg)
    results.append(value)
  if len(results) == 1:
    return results[0]
  return results




def get_optional_items(dictionary, optional_str, defaults):
  # Example optional_str: 'parent, line:i, lineIndex:i'
  if not isinstance(dictionary, dict):
    raise TypeError
  if not isinstance(optional_str, str):
    raise TypeError
  if not isinstance(defaults, tuple):
    raise TypeError
  optional_items = optional_str.split(', ')
  results = []
  types = {'i': int, 's': str}
  for i, item in enumerate(optional_items):
    default = defaults[i]
    if ':' in item:
      key, value_type_char = item.split(':')
      value_type = types[value_type_char]
    else:
      key = item
      value_type = None
    if key in dictionary:
      value = dictionary[key]
    else:
      value = default
    if value_type is not None:
      if not isinstance(value, value_type):
        msg = "Optional dictionary item '{k}' found but is not a '{t}', as was specified. Instead, it is a '{t2}'.".format(k=key, t=value_type.__name__, t2=type(value).__name__)
        raise TypeError(msg)
    results.append(value)
  if len(results) == 1:
    return results[0]
  return results




def stop(msg=None):
  if msg: print "\n%s\n"%msg
  import sys; sys.exit()
