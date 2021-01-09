import os
import logging
import colorlog


def configureModuleLogger(args):
	logger = args.logger
	logLevel = 'error' # default
	if 'logLevel' in args:
		logLevel = args.logLevel # override
	logLevels = {
		'error': logging.ERROR,
		'warning': logging.WARNING,
		'info': logging.INFO,
		'debug': logging.DEBUG,
	}
	logLevel = logLevels[logLevel]
	logger.setLevel(logLevel)
	# Construct logFormat.
	# Example logFormat:
	# '%(asctime)s %(levelname)-8s [%(name)s: %(lineno)s (%(funcName)s)] %(message)s'
	# Example logLine:
	# 2020-11-19 13:14:10 DEBUG    [demo1.basic: 19 (hello)] Entered into basic.hello.
	loggerName = '%(name)s' # default
	if 'loggerName' in args:
		loggerName = args.loggerName # override
	logFormat = '[' + loggerName + ': %(lineno)s (%(funcName)s)] %(message)s'
	# Note: In "%(levelname)-8s", the '8' pads the levelname length with spaces up to 8 characters, and the hyphen left-aligns the levelname.
	logFormat = '%(levelname)-8s ' + logFormat
	if 'logTimestamp' in args and args.logTimestamp == True:
		logFormat = '%(asctime)s ' + logFormat
	logFormatter = logging.Formatter(fmt = logFormat, 
		datefmt = '%Y-%m-%d %H:%M:%S')
	# Set up console handler.
	# 1) Standard console handler:
	#consoleHandler = logging.StreamHandler()
	#consoleHandler.setLevel(logLevel)
	#consoleHandler.setFormatter(logFormatter)
	#logger.addHandler(consoleHandler)
	# 2) Colored console handler:
	consoleHandler2 = colorlog.StreamHandler()
	logFormatColor = logFormat.replace('%(levelname)', '%(log_color)s%(levelname)')
	logFormatColor = logFormatColor.replace('%(message)', '%(message_log_color)s%(message)')
	# Example logFormatColor:
	# '%(asctime)s %(log_color)s%(levelname)-8s [%(name)s: %(lineno)s (%(funcName)s)] %(message_log_color)s%(message)s'
	logFormatter2 = colorlog.ColoredFormatter(
		logFormatColor,
		datefmt='%Y-%m-%d %H:%M:%S',
		reset=True, # Clear all formatting (both foreground and background colors).
		# log_colors controls the base text color for particular log levels.
		# A second comma-separated value, if provided, controls the background color.
		log_colors={
			'DEBUG':    'blue',
			'INFO':     'green',
			'WARNING':  'yellow',
			'ERROR':    'red',
			'CRITICAL': 'red,bg_white',
		},
		# secondary_log_colors controls the value of message_log_color.
		# If a level is commented out, the message text will have the base text color (which is set in log_colors).
		secondary_log_colors={
			'message': {
				'DEBUG':    'white',
				#'INFO':     'white',
				'WARNING':  'white',
				'ERROR':    'white',
				'CRITICAL': 'white',
			}
		},
	)
	consoleHandler2.setFormatter(logFormatter2)
	logger.addHandler(consoleHandler2)
	# Set up file handler.
	if 'logFilePath' in args and args.logFilePath != None:
		logFilePath = args.logFilePath
		# Create logFile directory if it doesn't exist.
		logDirPath = os.path.dirname(logFilePath)
		if logDirPath != '':
			if not os.path.exists(logDirPath):
				os.makedirs(logDirPath)
		# Note: If log file already exists, new log lines will be appended to it.
		fileHandler = logging.FileHandler(logFilePath, mode='a', delay=True)
		# If delay is true, then file opening is deferred until the first call to emit().
		fileHandler.setLevel(logLevel)
		fileHandler.setFormatter(logFormatter)
		logger.addHandler(fileHandler)
