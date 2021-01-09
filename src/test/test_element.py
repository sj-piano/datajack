import pytest
from argparse import Namespace as NS
from .. import code, util
Element = code.Element.Element
Entry = code.Element.Entry




# Notes:
# - "work directory" = directory that contains this file.
# - Running the command {pytest test_create_transaction_4.py} in the work directory should load and run the tests in this file.
# - Run a specific test:
# -- pytest test_create_transaction_4.py::test_arg_none
# - Run quietly:
# -- pytest -q test_create_transaction_4.py
# - Print log data during a single test:
# -- pytest -o log_cli=true --log-cli-level=DEBUG --log-format="%(levelname)s [%(lineno)s: %(funcName)s] %(message)s" test_create_transaction_4.py::test_arg_none
# -- This is very useful when you want to manually check the operation of the functions during the test.




### TEST SECTION
# Basic checks.
def test_hello():
	e = Element()
	assert e.hello() == 'world'



### TEST SECTION
# Basic domain checks.











if __name__ == '__main__':
	main()
