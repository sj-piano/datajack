# Imports
from argparse import Namespace




# Relative imports
from . import module_logger
from . import validate




def setup(args=Namespace()):
  # Set up the modules in this package.
  validate.setup(args)

