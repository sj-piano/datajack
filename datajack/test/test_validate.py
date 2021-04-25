# Imports
import pytest




# Relative imports
from .. import util




# Shortcuts
v = util.validate




# ### SECTION
# Integer validation.


def test_string_is_positive_integer():
  v.spi('1')


def test_string_is_positive_integer_2():
  pytest.raises(TypeError, v.spi, 1)


def test_string_is_positive_integer_3():
  pytest.raises(ValueError, v.spi, '-1')


def test_string_is_positive_integer_4():
  v.spi('17984123795672347508973451')


def test_string_is_positive_integer_5():
  pytest.raises(ValueError, v.spi, '123abc')


def test_string_is_positive_integer_6():
  pytest.raises(ValueError, v.spi, '0')


def test_string_is_whole_number():
  v.swn('1')


def test_string_is_whole_number():
  v.swn('0')


def test_string_is_decimal():
  v.sd('0.00000000', dp=8)


def test_string_is_decimal_2():
  pytest.raises(ValueError, v.sd, '0', dp=2)


def test_string_is_decimal_3():
  v.sd('1.234', dp=3)


def test_string_is_decimal_4():
  pytest.raises(ValueError, v.sd, '0.2.3.4', dp=4)


def test_string_is_decimal_5():
  pytest.raises(ValueError, v.sd, 'foo', dp=4)


def test_string_is_decimal_6():
  pytest.raises(TypeError, v.sd, 123, dp=4)




# ### SECTION
# Date validation.


def test_date():
  v.validate_string_is_date('1970-01-01')


def test_date_2():
  pytest.raises(ValueError, v.validate_string_is_date, 'foo')


def test_date_3():
  pytest.raises(ValueError, v.validate_string_is_date, '1970-01-1')
