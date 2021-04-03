# Imports
import os
import logging
import argparse




# Shortcuts
Namespace = argparse.Namespace




# Non-standard-library imports
colorLogImported = False
try:
  import colorlog
  colorLogImported = True
except:
  colorLogImported = False




def configureModuleLogger(a1):
  a = Namespace(**vars(a1))
  logger = a.logger
  logger.propagate = False
  logLevel = a.logLevel if 'logLevel' in a else 'error'
  logLevel = 'debug' if 'debug' in a and a.debug else logLevel
  logLevels = {
    'error': logging.ERROR,
    'warning': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG,
  }
  logLevel = logLevels[logLevel]
  logger.setLevel(logLevel)
  # Add a convenience method.
  def setLevelStr(logLevelStr):
    logLevel = logLevels[logLevelStr]
    logger.setLevel(logLevel)
  logger.setLevelStr = setLevelStr
  # Construct logFormat.
  # Example logFormat:
  # '%(asctime)s %(levelname)-8s [%(name)s: %(lineno)s (%(funcName)s)] %(message)s'
  # Example logLine:
  # 2020-11-19 13:14:10 DEBUG    [demo1.basic: 19 (hello)] Entered into basic.hello.
  loggerName = a.loggerName if 'loggerName' in a else '%(name)s'
  logFormat = '[' + loggerName + ': %(lineno)s (%(funcName)s)] %(message)s'
  # Note: In "%(levelname)-8s", the '8' pads the levelname length with spaces up to 8 characters, and the hyphen left-aligns the levelname.
  logFormat = '%(levelname)-8s ' + logFormat
  if 'logTimestamp' in a and a.logTimestamp:
    logFormat = '%(asctime)s ' + logFormat
  logFormatter = logging.Formatter(fmt = logFormat,
    datefmt = '%Y-%m-%d %H:%M:%S')
  logFormatter2 = None
  if colorLogImported:
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
          'DEBUG':    'blue',
          #'INFO':     'white',
          'WARNING':  'white',
          'ERROR':    'white',
          'CRITICAL': 'white',
        }
      },
    )
  # Set up console handler.
  # 1) Standard console handler:
  if not colorLogImported:
    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logLevel)
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)
  else:
  # 2) Colored console handler:
    consoleHandler2 = colorlog.StreamHandler()
    consoleHandler2.setLevel(logLevel)
    consoleHandler2.setFormatter(logFormatter2)
    logger.addHandler(consoleHandler2)
  # Set up file handler.
  if 'logFilePath' in a and a.logFilePath:
    logFilePath = a.logFilePath
    # Create logFile directory if it doesn't exist.
    logDirPath = os.path.dirname(logFilePath)
    if logDirPath != '':
      if not os.path.exists(logDirPath):
        os.makedirs(logDirPath)
    # Note: If log file already exists, new log lines will be appended to it.
    fileHandler = logging.FileHandler(logFilePath, mode='a', delay=True)
    # If delay is true, then file opening is deferred until the first call to emit().
    fileHandler.setLevel(logLevel)
    # It turns out that the colorLog formatter's ANSI escape codes work in 'cat' & 'tail' (but not vim).
    # 'less' can, with the -R flag.
    # To display in vim, strip the escape chars: $ sed 's|\x1b\[[;0-9]*m||g' somefile | vim -
    if not colorLogImported:
      fileHandler.setFormatter(logFormatter)
    else:
      fileHandler.setFormatter(logFormatter2)
    logger.addHandler(fileHandler)
