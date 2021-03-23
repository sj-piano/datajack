#!/usr/bin/python




# Imports
import sys
import argparse
import os
import logging
import time
import json




# Local imports
import src




# Shortcuts
Namespace = argparse.Namespace
join = os.path.join
isfile = os.path.isfile




# Set up logger for this module. By default, it produces no output.
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
log = logger.info
deb = logger.debug




def main():

	epilogString = ''

	parser = argparse.ArgumentParser(
		description='Command-Line Interface (CLI) for using the datajack package.',
		epilog=epilogString,
	)
	
	parser.add_argument(
		'-t', '--task', 
		help="Task to perform (default: '%(default)s').",
		default='hello',
	)	

	parser.add_argument(
		'-l', '--logLevel', type=str,
		choices=['debug', 'info', 'warning', 'error'],
		help="Choose logging level (default: '%(default)s').",
		default='info',
	)

	parser.add_argument(
		'-d', '--debug',
		action='store_true',
		help="Sets logLevel to 'debug'. This overrides --logLevel.",
	)

	a = parser.parse_args()

	# Setup
	setup(a)

	# Run top-level function (i.e. the appropriate task).
	if a.task == 'hello':
		hello(a)
	else:
		msg = "Unrecognised task: {}".format(a.task)
		raise ValueError(msg)




def setup(a=Namespace()): # a = arguments.
	a.logger = logger
	a.loggerName = 'cli'
	# Configure logger for this script.
	src.util.moduleLogger.configureModuleLogger(a)
	# Configure logging levels for datajack package.
	# - By default, it does no logging.
	# - If src.setup() is run without an argument, it has error-level logging.
	src.setup(a)
	# It's possible to configure logging separately for individual modules, with or without running src.setup().
	#src.code.Element.setup(Namespace(logLevel='error'))
	log('Setup complete.')
	deb('Logger is printing debug output.')




def hello(a):
	print 'world'





if __name__ == '__main__':
	main()




