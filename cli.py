#!/usr/bin/python3




# Imports
import os
import sys
import argparse
import logging




# Local imports
# (Can't use relative imports because this is a top-level script)
import datajack




# Shortcuts
Element = datajack.code.Element.Element
Entry = datajack.code.Element.Entry




# Notes:
# - Using keyword function arguments, each of which is on its own line,
# makes Python code easier to maintain. Arguments can be changed and
# rearranged much more easily.




# Set up logger for this module. By default, it logs at ERROR level.
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
logger.setLevel(logging.ERROR)
log = logger.info
deb = logger.debug




def setup(
    log_level = 'error',
    debug = False,
    log_timestamp = False,
    log_filepath = None,
    ):
  logger_name = 'cli'
  # Configure logger for this module.
  datajack.util.module_logger.configure_module_logger(
    logger = logger,
    logger_name = logger_name,
    log_level = log_level,
    debug = debug,
    log_timestamp = log_timestamp,
    log_filepath = log_filepath,
  )
  deb('Setup complete.')
  # Configure logging levels for datajack package.
  # By default, without setup, it produces no log output.
  # Optionally, the package could be configured here to use a different log level, by e.g. passing in 'error' instead of log_level.
  datajack.setup(
    log_level = log_level,
    debug = debug,
    log_timestamp = log_timestamp,
    log_filepath = log_filepath,
  )




def main():

  parser = argparse.ArgumentParser(
    description='Command-Line Interface (CLI) for using the datajack package.'
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

  parser.add_argument(
    '-s', '--logTimestamp',
    action='store_true',
    help="Choose whether to prepend a timestamp to each log line.",
  )

  parser.add_argument(
    '-o', '--logToFile',
    action='store_true',
    help="Choose whether to save log output to a file.",
  )

  parser.add_argument(
    '-p', '--logFilepath',
    help="The path to the file that log output will be written to.",
    default='log_edgecase_client.txt',
  )

  a = parser.parse_args()

  log_filepath = a.logFilepath if a.logToFile else None

  # Setup
  setup(
    log_level = a.logLevel,
    debug = a.debug,
    log_timestamp = a.logTimestamp,
    log_filepath = log_filepath,
  )

  # Run top-level function (i.e. the appropriate task).
  tasks = 'hello basic valid test'.split()
  if a.task not in tasks:
    print("Unrecognised task: {}".format(a.task))
    stop()
  globals()[a.task](a)  # run task.




def hello(a):
  e = Element()
  value = e.hello()
  assert value == 'world'
  print(value)




def basic(a):
  input = '<hello>mars</hello>'
  e = Element.from_string(data=input)
  assert e.text == 'mars'




def valid(a):
  location = "cli.py:valid()"
  v = datajack.util.validate
  foo = 123
  v.s(foo, 'foo', location)




def test(a):
  d = """
<list>
<title>Fruit</title>
<item>Orange</item>
<item>Apple</item>
</list>
"""
  e = Element.from_string(data=d.strip(), verbose=True)




def stop(msg=None):
  if msg is not None:
    print(msg)
  import sys
  sys.exit()




if __name__ == '__main__':
  main()
