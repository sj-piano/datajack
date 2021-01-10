import pytest
from argparse import Namespace as NS
from .. import code, util
Element = code.Element.Element
Entry = code.Element.Entry
import logging


# Set up logger for this module.
logger = logging.getLogger(__name__)
log = logger.info
deb = logger.debug




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




### SECTION
# Basic checks.


def test_hello():
	e = Element()
	assert e.hello() == 'world'


def test_hello_2():
	d = "<hello>world</hello>"
	e = Element.fromString(data=d)
	assert e.text == 'world'




### SECTION
# Data fixtures


@pytest.fixture(scope="module")
def e1():
	d = """<list>
<title>Fruit</title>
<item>Orange</item>
<item>Apple</item>
<item>Cake</item>
<sublist>
<title>Planets</title>
<planet>1<name>Mercury</name></planet>
<planet>2<name>Venus</name></planet>
<planet>3<name>Earth</name></planet>
<planet>4<name>Mars</name></planet>
</sublist>
<languages>
<language><category>Python</category><version>2</version></language>
<language><category>Python</category><version>3</version></language>
</languages>
</list>
"""
	code.Element.setup(NS(logLevel='info'))
	e1 = Element.fromString(data=d.strip())
	code.Element.setup(NS(logLevel='debug'))
	yield e1




### SECTION
# Basic xpath checks



def test_xpath_1(e1):
	xpath = 'title'
	e2 = e1.get(xpath)[0]
	assert e2.value == 'Fruit'


def test_xpath_2(e1):
	xpath = '@item'
	e_list = e1.get(xpath)
	assert len(e_list) == 3
	e_values = sorted([e.value for e in e_list])
	assert e_values == sorted('Orange Apple Cake'.split())


def test_xpath_3(e1):
	xpath = 'sublist/title'
	e2 = e1.get(xpath)[0]
	assert e2.value == 'Planets'


def test_xpath_4(e1):
	xpath = 'sublist/@planet'
	e_list = e1.get(xpath)
	assert len(e_list) == 4
	e_texts = sorted([e.text for e in e_list])
	assert e_texts == sorted('1 2 3 4'.split())


def test_xpath_5(e1):
	xpath = 'sublist/@planet/name'
	e_list = e1.get(xpath)
	assert len(e_list) == 4
	e_values = sorted([e.value for e in e_list])
	assert e_values == sorted('Mercury Venus Earth Mars'.split())


def test_xpath_6(e1):
	xpath = '//@name'
	e_list = e1.get(xpath)
	assert len(e_list) == 4
	e_values = sorted([e.value for e in e_list])
	assert e_values == sorted('Mercury Venus Earth Mars'.split())


def test_xpath_7(e1):
	xpath = "sublist[title='Planets']"
	e_list = e1.get(xpath)
	assert len(e_list) == 1
	e2 = e_list[0]
	assert e2.name == 'sublist'
	assert e2.getOne('title').value == 'Planets'


def test_xpath_8(e1):
	xpath = "languages/@language[category='Python']"
	e_list = e1.get(xpath)
	assert len(e_list) == 2
	versions = [e.getOne('version').value for e in e_list]
	assert sorted(versions) == ['2','3']








if __name__ == '__main__':
	main()
