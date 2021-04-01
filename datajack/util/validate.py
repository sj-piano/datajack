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

date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
hex_digits = '0123456789abcdef'



### SECTION
# Basic validation functions.




def validateHexLength(s, n):
  validateHex(s)
  if not isinstance(n, int): raise TypeError
  # 1 byte is 2 hex chars.
  if len(s) != n*2:
    raise ValueError


def validateHex(s):
  if not isinstance(s, str): raise TypeError
  if not all(c in hex_digits for c in s):
    raise ValueError


def vD(s, dp=2):
  validateDecimal(s, dp)


def validateDecimal(s, dp=2):
  if not isinstance(s, str): raise TypeError
  if not isinstance(dp, int): raise TypeError
  regex = r'^\d*.\d{%d}$' % dp
  decimal_pattern = re.compile(regex)
  if not decimal_pattern.match(s):
    raise ValueError('{s} is not a valid {d}-place decimal.'.format(s=repr(s), d=dp))


def vWN(s):
  validateWholeNumber(s)


def validateWholeNumber(s):
  # 0 is a whole number.
  if not isinstance(s, str): raise TypeError
  if s == '0': return
  validatePositiveInteger(s)


def vPI(s):
  validatePositiveInteger(s)


def validatePositiveInteger(s):
  if not isinstance(s, str): raise TypeError
  if s == '0': raise ValueError('0 is not a positive number.')
  if not s.isdigit():
    raise ValueError('{} does not contain only digits.'.format(repr(s)))


def validateDate(s):
  if not isinstance(s, str): raise TypeError
  # https://stackoverflow.com/a/45598540
  if not date_pattern.match(s):
    raise ValueError('{} is not a valid date.'.format(repr(s)))







