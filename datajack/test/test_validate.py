# Imports
import pytest
import logging



# Relative imports
from .. import util




# Shortcuts
v = util.validate




# Set up logger for this module.
logger = logging.getLogger(__name__)
log = logger.info
deb = logger.debug




### SECTION
# Integer validation.


def test_validate_string_is_positive_integer():
  v.v_spi('1')


def test_validate_string_is_positive_integer_2():
  pytest.raises(TypeError, v.v_spi, 1)


def test_validate_string_is_positive_integer_3():
  pytest.raises(ValueError, v.v_spi, '-1')


def test_validate_string_is_positive_integer_4():
  v.v_spi('17984123795672347508973451')


def test_validate_string_is_positive_integer_5():
  pytest.raises(ValueError, v.v_spi, '123abc')


def test_validate_string_is_positive_integer_6():
  pytest.raises(ValueError, v.v_spi, '0')


def test_validate_string_is_whole_number():
  v.v_swn('1')


def test_validate_string_is_whole_number():
  v.v_swn('0')


def test_validate_string_is_decimal():
  v.v_sd('0.00000000', dp=8)


def test_validate_string_is_decimal_2():
  pytest.raises(ValueError, v.v_sd, '0', dp=2)


def test_validate_string_is_decimal_3():
  v.v_sd('1.234', dp=3)


def test_validate_string_is_decimal_4():
  pytest.raises(ValueError, v.v_sd, '0.2.3.4', dp=4)


def test_validate_string_is_decimal_5():
  pytest.raises(ValueError, v.v_sd, 'foo', dp=4)


def test_validate_string_is_decimal_6():
  pytest.raises(TypeError, v.v_sd, 123, dp=4)




### SECTION
# Date validation.


def test_validate_date():
  v.validate_string_is_date('1970-01-01')


def test_validate_date_2():
  pytest.raises(ValueError, v.validate_string_is_date, 'foo')


def test_validate_date_3():
  pytest.raises(ValueError, v.validate_string_is_date, '1970-01-1')





