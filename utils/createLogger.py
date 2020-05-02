#!/usr/bin/python




import os
import logging
from DotDictionary import DotDict




def main():
	loggerSettings = {
		'name': 'testLogger',
		'level': 'debug',
		'filepath': 'testLogger.log',
		'timestamp': True,
		'logToConsole': True,
	}
	testLogger = createLogger(loggerSettings)
	#testLogger.info('hello world') # will create a log file 'testLogger.log'
	settings2 = {'name': 'testLogger2', 'level': 'info'}
	testLogger2 = createLogger(settings2)
	testLogger2.info('hello planet')




def createLogger(settings):
	# Validate input.
	if not isinstance(settings, dict):
		raise TypeError("settings must be a dictionary.")
	s = DotDict(settings)
	keys = s.keys()
	if 'name' not in keys or 'level' not in keys:
		raise TypeError("At a minimum, settings must contain 'name' and 'level' keys.")
	if not isinstance(s.name, str):
		raise TypeError("'name' must be a string.")
	logLevels = {
		'critical': logging.CRITICAL,
		'error': logging.ERROR,
		'warning': logging.WARNING,
		'info': logging.INFO,
		'debug': logging.DEBUG,
		'notset': logging.NOTSET
	}
	if s.level not in logLevels.keys():
		msg = "'level' must be in this list: " + str(sorted(list(logLevels.keys())))
		raise ValueError(msg)
	# Validate optional input.
	options = {
		'filepath': str,
		'timestamp': bool,
		'logToConsole': bool,
	}
	for oName, oType in options.items():
		if oName in s:
			if not isinstance(s[oName], oType):
				raise TypeError("'{n}', if present, must be a {t}.".format(n=oName, t=oType.__name__))
	# Defaults.
	if 'logToConsole' not in s:
		s.logToConsole = True
	if 'timestamp' not in s:
		s.timestamp = False
	if 'filepath' not in s:
		s.filepath = None
	if not (s.logToConsole or s.filepath):
		raise ValueError("if 'logToConsole' is False, then 'filepath' must be present.")
	# Create logger.
	logger = logging.getLogger(s.name)
	level = logLevels[s.level]
	logger.setLevel(level)
	# Create formatter.
	if s.timestamp:
		formatter = logging.Formatter(
			fmt = '%(asctime)s [%(levelname)s] [%(name)s] - %(message)s',
			datefmt = '%Y-%m-%d %H:%M:%S'
		)
	else:
		formatter = logging.Formatter(
			fmt = '[%(levelname)s] [%(name)s] - %(message)s',
			datefmt = '%Y-%m-%d %H:%M:%S'
		)
	# Create console handler if specified in settings.
	if s.logToConsole:
		ch = logging.StreamHandler()
		ch.setLevel(level)
		ch.setFormatter(formatter)
		logger.addHandler(ch)
	# Create file handler if specified in settings.
	if s.filepath:
		# Create filepath directory path if it doesn't exist.
		dPath = os.path.dirname(s.filepath)
		if dPath != '':
			if not os.path.exists(dPath):
				os.makedirs(dPath)
		fh = logging.FileHandler(s.filepath, mode='a', delay=True)
		# Note: If log file already exists, new log lines will be appended to it.
		fh.setLevel(level)
		fh.setFormatter(formatter)
		logger.addHandler(fh)
	return logger




def stop(msg=None):
	if msg: print "\n%s\n" % msg
	import sys; sys.exit()




if __name__ == '__main__':
	main()
