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
# Date validation.


def test_validate_date():
	v.validateDate('1970-01-01')


def test_validate_date_2():
	pytest.raises(ValueError, v.validateDate, 'foo')


def test_validate_date_3():
	pytest.raises(ValueError, v.validateDate, '1970-01-1')





