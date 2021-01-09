import Datajack, Element
from argparse import Namespace


def setup(args=Namespace()):
	# Set up the modules in this directory.
	Datajack.setup(args)
	Element.setup(args)
