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



def loadOrCreateLogger(parameters, loggerName):
	# Load logger from the loggers storage if it's present.
	# Otherwise, create a new logger so that the existing code still works (e.g. logger.info calls).
	if not isinstance(parameters, dict):
		raise TypeError
	if not isinstance(loggerName, str):
		raise TypeError
	logger = None
	if 'loggers' in parameters:
		for existingLogger in parameters['loggers']:
			if existingLogger.name == loggerName:
				logger = existingLogger
	if logger is None:
		logger = createLogger({'name':loggerName, 'level':'error'})
	log = logger.info
	deb = logger.debug
	return [logger, log, deb]




def createLogger(settings):
	# Validate input.
	if not isinstance(settings, dict):
		raise TypeError("settings must be a dictionary.")
	s = DotDict(settings)
	required = ('name', 'level')
	if not all(k in s.keys() for k in required):
		raise TypeError("Required keys: {r}".format(r=required))
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
	for optionName, optionType in options.items():
		if optionName in s:
			if not isinstance(s[optionName], optionType):
				raise TypeError("Option '{n}' must be a {t}.".format(n=optionName, t=optionType.__name__))
	# Defaults.
	if 'logToConsole' not in s:
		s.logToConsole = True
	if 'timestamp' not in s:
		s.timestamp = False
	if 'filepath' not in s:
		s.filepath = None
	if not (s.logToConsole or s.filepath):
		raise ValueError("At least one of the options 'logToConsole' and 'filepath' must be used. logToConsole is True by default.")
	# Create logger.
	logger = logging.getLogger(s.name)
	level = logLevels[s.level]
	logger.setLevel(level)
	# Create formatter.
	if s.timestamp:
		formatter = logging.Formatter(
			fmt = '%(asctime)s %(levelname)s [%(name)s] - %(message)s',
			datefmt = '%Y-%m-%d %H:%M:%S'
		)
	else:
		formatter = logging.Formatter(
			fmt = '%(levelname)s [%(name)s] - %(message)s',
			datefmt = '%Y-%m-%d %H:%M:%S'
		)
	# Create console handler if specified in settings.
	if s.logToConsole:
		consoleHandler = logging.StreamHandler()
		consoleHandler.setLevel(level)
		consoleHandler.setFormatter(formatter)
		logger.addHandler(consoleHandler)
	# Create file handler if specified in settings.
	if s.filepath:
		# Create filepath directory path if it doesn't exist.
		dPath = os.path.dirname(s.filepath)
		if dPath != '':
			if not os.path.exists(dPath):
				os.makedirs(dPath)
		fileHandler = logging.FileHandler(s.filepath, mode='a', delay=True)
		# Note: If log file already exists, new log lines will be appended to it.
		fileHandler.setLevel(level)
		fileHandler.setFormatter(formatter)
		logger.addHandler(fileHandler)
	return logger



def stop(msg=None):
	if msg: print "\n%s\n" % msg
	import sys; sys.exit()




if __name__ == '__main__':
	main()
