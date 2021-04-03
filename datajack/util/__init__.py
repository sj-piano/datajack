from argparse import Namespace
import module_logger
import validate




def setup(args=Namespace()):
  # Set up the modules in this package.
  validate.setup(args)
