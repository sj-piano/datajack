# Imports
from argparse import Namespace




# Relative imports
from . import Element




def setup(args=Namespace()):
  # Set up the modules in this directory.
  Element.setup(args)

