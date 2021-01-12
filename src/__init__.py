import code, util
from argparse import Namespace


def setup(args=Namespace()):
	# Set up the modules in this package.
	code.setup(args)
	util.setup(args)
