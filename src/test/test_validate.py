import pytest
from argparse import Namespace as NS
from .. import util
import logging
v = util.validate


# Set up logger for this module.
logger = logging.getLogger(__name__)
log = logger.info
deb = logger.debug



### SECTION
# Integer validation.


def test_validate_positive_integer():
  v.vPI('1')


def test_validate_positive_integer_2():
  pytest.raises(TypeError, v.vPI, 1)


def test_validate_positive_integer_3():
  pytest.raises(ValueError, v.vPI, '-1')


def test_validate_positive_integer_4():
  v.vPI('17984123795672347508973451')


def test_validate_positive_integer_5():
  pytest.raises(ValueError, v.vPI, '123abc')


def test_validate_positive_integer_6():
  pytest.raises(ValueError, v.vPI, '0')


def test_validate_whole_number():
  v.vWN('1')


def test_validate_whole_number():
  v.vWN('0')


def test_validate_decimal():
  v.vD('0.00000000', dp=8)


def test_validate_decimal_2():
  pytest.raises(ValueError, v.vD, '0', dp=2)


def test_validate_decimal_3():
  v.vD('1.234', dp=3)


def test_validate_decimal_4():
  pytest.raises(ValueError, v.vD, '0.2.3.4', dp=4)


def test_validate_decimal_5():
  pytest.raises(ValueError, v.vD, 'foo', dp=4)


def test_validate_decimal_6():
  pytest.raises(TypeError, v.vD, 123, dp=4)




### SECTION
# Date validation.


def test_validate_date():
  v.validateDate('1970-01-01')


def test_validate_date_2():
  pytest.raises(ValueError, v.validateDate, 'foo')


def test_validate_date_3():
  pytest.raises(ValueError, v.validateDate, '1970-01-1')





