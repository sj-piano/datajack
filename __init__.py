import src
from argparse import Namespace
import logging


# Collect up the things that we want in the immediate namespace of the imported datajack module.
# E.g. datajack.Element()
Element = src.code.Element.Element
Entry = src.code.Element.Entry




# Set up logger for this module. By default, it produces no output.
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
log = logger.info
deb = logger.debug




def setup(a=Namespace()): # a = arguments.
	a.logger = logger
	a.loggerName = 'datajack'
	if 'debug' not in a:
		a.debug = False
	if 'logTimestamp' not in a:
		a.logTimestamp = False
	if a.debug == True:
		a.logLevel = 'debug'
	# Configure logger for this script.
	src.util.moduleLogger.configureModuleLogger(a)
	# Configure logging levels for datajack package.
	# - By default, it does no logging.
	# - If src.setup() is run without an argument, it has error-level logging.
	a2 = Namespace(logLevel=a.logLevel, logTimestamp=a.logTimestamp)
	src.setup(a2)
	# It's possible to configure logging separately for individual modules, with or without running src.setup().
	#src.code.Element.setup(Namespace(logLevel='error'))
