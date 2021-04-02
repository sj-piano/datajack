# Imports
import inspect




# Global vars
types = {'b': bool, 'i': int, 's': str}




def confirm_no_args(args):
  caller_name = inspect.stack()[1][3]
  if not isinstance(args, tuple):
    raise TypeError
  if args != ():
    msg = "Function/method '{c}' doesn't accept positional args.".format(c=caller_name)
    raise ValueError(msg)




def stop(msg=None):
  if msg: print "\n%s\n"%msg
  import sys; sys.exit()
