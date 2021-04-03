# Imports
import os
import logging
import argparse




# Shortcuts
Namespace = argparse.Namespace




# Non-standard-library imports
colorlog_imported = False
try:
  import colorlog
  colorlog_imported = True
except:
  colorlog_imported = False




def configure_module_logger(a1):
  a = Namespace(**vars(a1))
  logger = a.logger
  logger.propagate = False
  log_level = a.log_level if 'log_level' in a else 'error'
  log_level = 'debug' if 'debug' in a and a.debug else log_level
  log_levels = {
    'error': logging.ERROR,
    'warning': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG,
  }
  log_level = log_levels[log_level]
  logger.setLevel(log_level)
  # Add a convenience method.
  def setLevel_str(log_level_str):
    log_level = log_levels[log_level_str]
    logger.setLevel(log_level)
  logger.setLevel_str = setLevel_str
  # Construct log_format.
  # Example log_format:
  # '%(asctime)s %(levelname)-8s [%(name)s: %(lineno)s (%(funcName)s)] %(message)s'
  # Example logLine:
  # 2020-11-19 13:14:10 DEBUG    [demo1.basic: 19 (hello)] Entered into basic.hello.
  logger_name = a.logger_name if 'logger_name' in a else '%(name)s'
  log_format = '[' + logger_name + ': %(lineno)s (%(funcName)s)] %(message)s'
  # Note: In "%(levelname)-8s", the '8' pads the levelname length with spaces up to 8 characters, and the hyphen left-aligns the levelname.
  log_format = '%(levelname)-8s ' + log_format
  if 'log_timestamp' in a and a.log_timestamp:
    log_format = '%(asctime)s ' + log_format
  log_formatter = logging.Formatter(fmt = log_format,
    datefmt = '%Y-%m-%d %H:%M:%S')
  log_formatter2 = None
  if colorlog_imported:
    log_format_color = log_format.replace('%(levelname)', '%(log_color)s%(levelname)')
    log_format_color = log_format_color.replace('%(message)', '%(message_log_color)s%(message)')
    # Example log_format_color:
    # '%(asctime)s %(log_color)s%(levelname)-8s [%(name)s: %(lineno)s (%(funcName)s)] %(message_log_color)s%(message)s'
    log_formatter2 = colorlog.ColoredFormatter(
      log_format_color,
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
  if not colorlog_imported:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)
  else:
  # 2) Colored console handler:
    console_handler2 = colorlog.StreamHandler()
    console_handler2.setLevel(log_level)
    console_handler2.setFormatter(log_formatter2)
    logger.addHandler(console_handler2)
  # Set up file handler.
  if 'log_file_path' in a and a.log_file_path:
    log_file_path = a.log_file_path
    # Create logFile directory if it doesn't exist.
    log_dir_path = os.path.dirname(log_file_path)
    if log_dir_path != '':
      if not os.path.exists(log_dir_path):
        os.makedirs(log_dir_path)
    # Note: If log file already exists, new log lines will be appended to it.
    file_handler = logging.file_handler(log_file_path, mode='a', delay=True)
    # If delay is true, then file opening is deferred until the first call to emit().
    file_handler.setLevel(log_level)
    # It turns out that the colorLog formatter's ANSI escape codes work in 'cat' & 'tail' (but not vim).
    # 'less' can, with the -R flag.
    # To display in vim, strip the escape chars: $ sed 's|\x1b\[[;0-9]*m||g' somefile | vim -
    if not colorlog_imported:
      file_handler.setFormatter(log_formatter)
    else:
      file_handler.setFormatter(log_formatter2)
    logger.addHandler(file_handler)
