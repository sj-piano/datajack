from argparse import Namespace
import misc, DotDictionary
import moduleLogger
import validate


def setup(args=Namespace()):
  # Set up the modules in this package.
  validate.setup(args)
