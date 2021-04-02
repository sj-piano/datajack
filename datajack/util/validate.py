# Imports
import logging
from argparse import Namespace
import re




# Relative imports
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

# https://stackoverflow.com/a/45598540
date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
hex_digits = '0123456789abcdef'




### SECTION
# Basic validation functions.
# Functions at the bottom are the most basic.
# Functions further up may use functions below them.




def wn(n):
  whole_number(n)


def whole_number(n):
  # 0 is a whole number.
  if n == 0:
    return
  positive_integer(n)


def pi(n):
  positive_integer(n)


def positive_integer(n):
  integer(n)
  if n < 0:
    raise ValueError


def i(n):
  integer(n)


def integer(n):
  if not isinstance(n, int):
    raise TypeError


def b(b):
  boolean(b)


def boolean(b):
  if type(b) != bool:
    raise TypeError


def hex_length(s, n):
  hex(s)
  if not isinstance(n, int):
    raise TypeError
  # 1 byte is 2 hex chars.
  if len(s) != n*2:
    raise ValueError


def hex(s):
  string(s)
  if not all(c in hex_digits for c in s):
    raise ValueError


def sd(s, dp=2):
  string_is_decimal(s, dp)


def string_is_decimal(s, dp=2):  # dp = decimal places
  string(s)
  if not isinstance(dp, int):
    raise TypeError
  regex = r'^\d*.\d{%d}$' % dp
  decimal_pattern = re.compile(regex)
  if not decimal_pattern.match(s):
    raise ValueError('{s} is not a valid {d}-place decimal.'.format(s=repr(s), d=dp))


def swn(s):
  string_is_whole_number(s)


def string_is_whole_number(s):
  # 0 is a whole number.
  string(s)
  if s == '0':
    return
  string_is_positive_integer(s)


def spi(s):
  string_is_positive_integer(s)


def string_is_positive_integer(s):
  string(s)
  if s == '0':
    raise ValueError('0 is not a positive number.')
  if not s.isdigit():
    raise ValueError('{} does not contain only digits.'.format(repr(s)))


def sdate(s):
  string_is_date(s)


def string_is_date(s):
  string(s)
  if not date_pattern.match(s):
    raise ValueError('{} is not a valid date.'.format(repr(s)))


def s(s):
  string(s)


def string(s):
  if not isinstance(s, str):
    raise TypeError



