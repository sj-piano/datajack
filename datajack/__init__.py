# Imports
from argparse import Namespace




# Relative imports
from . import code
from . import util




def setup(args=Namespace()):
  # Set up the modules in this package.
  code.setup(args)
  util.setup(args)

