import logging
from argparse import Namespace
import re
from . import moduleLogger




# Set up logger for this module. By default, it produces no output.
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
log = logger.info
deb = logger.debug


def setup(args=Namespace()):
	args.logger = logger
	# Configure logger for this module.
	moduleLogger.configureModuleLogger(args)




### SECTION
# Components.

date_pattern = re.compile(r'\d{4}-\d{2}-\d{2}')




### SECTION
# Basic validation functions.


def validateDate(s):
	# https://stackoverflow.com/a/45598540
	if not date_pattern.match(s):
		raise ValueError











