#!/usr/bin/python3




# Imports
import sys
import argparse
import os
import logging
import time
import json




# Local imports
import datajack




# Shortcuts
Namespace = argparse.Namespace
join = os.path.join
isfile = os.path.isfile
Element = datajack.code.Element.Element
Entry = datajack.code.Element.Entry




# Set up logger for this module. By default, it produces no output.
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
log = logger.info
deb = logger.debug




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

  a = parser.parse_args()

  # Setup
  setup(a)

  # Run top-level function (i.e. the appropriate task).
  if a.task == 'hello':
    hello(a)
  elif a.task == 'basic':
    basic(a)
  elif a.task == 'valid':
    valid(a)
  elif a.task == 'test':
    test(a)
  else:
    msg = "Unrecognised task: {}".format(a.task)
    raise ValueError(msg)




def setup(a=Namespace()):  # a = arguments.
  a.logger = logger
  a.loggerName = 'cli'
  # Configure logger for this script.
  datajack.util.module_logger.configure_module_logger(a)
  # Configure logging levels for datajack package.
  # - By default, it does no logging.
  # - If datajack.setup() is run without an argument, it has error-level logging.
  datajack.setup(a)
  # It's possible to configure logging separately for individual modules, with or without running datajack.setup().
  #datajack.code.Element.setup(Namespace(logLevel='error'))
  log('Setup complete.')
  deb('Logger is printing debug output.')




def hello(a):
  e = Element()
  assert e.hello() == 'world'




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




if __name__ == '__main__':
  main()



