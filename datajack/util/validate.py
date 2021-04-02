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




def v_wn(n):
  validate_whole_number(n)


def validate_whole_number(n):
  # 0 is a whole number.
  if n == 0:
    return
  validate_positive_integer(n)


def v_pi(n):
  validate_positive_integer(n)


def validate_positive_integer(n):
  validate_integer(n)
  if n < 0:
    raise ValueError


def v_i(n):
  validate_integer(n)


def validate_integer(n):
  if not isinstance(n, int):
    raise TypeError


def v_b(b):
  validate_boolean(b)


def validate_boolean(b):
  if type(b) != bool:
    raise TypeError


def validate_hex_length(s, n):
  validate_hex(s)
  if not isinstance(n, int):
    raise TypeError
  # 1 byte is 2 hex chars.
  if len(s) != n*2:
    raise ValueError


def validate_hex(s):
  validate_string(s)
  if not all(c in hex_digits for c in s):
    raise ValueError


def v_sd(s, dp=2):
  validate_string_is_decimal(s, dp)


def validate_string_is_decimal(s, dp=2):  # dp = decimal places
  validate_string(s)
  if not isinstance(dp, int):
    raise TypeError
  regex = r'^\d*.\d{%d}$' % dp
  decimal_pattern = re.compile(regex)
  if not decimal_pattern.match(s):
    raise ValueError('{s} is not a valid {d}-place decimal.'.format(s=repr(s), d=dp))


def v_swn(s):
  validate_string_is_whole_number(s)


def validate_string_is_whole_number(s):
  # 0 is a whole number.
  validate_string(s)
  if s == '0':
    return
  validate_string_is_positive_integer(s)


def v_spi(s):
  validate_string_is_positive_integer(s)


def validate_string_is_positive_integer(s):
  validate_string(s)
  if s == '0':
    raise ValueError('0 is not a positive number.')
  if not s.isdigit():
    raise ValueError('{} does not contain only digits.'.format(repr(s)))


def v_sdate(s):
  validate_string_is_date(s)


def validate_string_is_date(s):
  validate_string(s)
  if not date_pattern.match(s):
    raise ValueError('{} is not a valid date.'.format(repr(s)))


def v_s(s):
  validate_string(s)


def validate_string(s):
  if not isinstance(s, str):
    raise TypeError



