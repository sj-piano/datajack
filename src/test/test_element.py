# Imports
import pytest
from argparse import Namespace as NS
import logging




# Relative imports
from .. import code
from .. import util




# Shortcuts
Element = code.Element.Element
Entry = code.Element.Entry




# Set up logger for this module.
logger = logging.getLogger(__name__)
log = logger.info
deb = logger.debug




# Notes:
# - "work directory" = directory that contains this file.
# - Running the command {pytest src/test/test_element.py} in the work directory should load and run the tests in this file.
# - Run a specific test:
# -- pytest src/test/test_element.py::test_hello
# - Run quietly:
# -- pytest -q src/test/test_element.py
# - Print log data during a single test:
# -- pytest -o log_cli=true --log-cli-level=DEBUG --log-format="%(levelname)s [%(lineno)s: %(funcName)s] %(message)s" src/test/test_element.py::test_hello
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


@pytest.fixture(scope="module")
def e2():
	d = """
<foo>hello
<bar>mars<bas>ASD</bas></bar>
</foo>
"""
	code.Element.setup(NS(logLevel='info'))
	e2 = Element.fromString(data=d.strip())
	code.Element.setup(NS(logLevel='debug'))
	yield e2


@pytest.fixture(scope="function")
def e3():
	d = """
<list>
<title>Fruit</title>
<item>Orange</item>
<item>Apple</item>
</list>
"""
	code.Element.setup(NS(logLevel='info'))
	e3 = Element.fromString(data=d.strip())
	code.Element.setup(NS(logLevel='debug'))
	yield e3




### SECTION
# CRUD tests


def test_get(e3):
	xpath = 'title'
	e = e3.getOne(xpath)
	assert e.value == 'Fruit'


def test_get_2(e3):
	xpath = 'item'
	e_values = [e.value for e in e3.getAll(xpath)]
	assert sorted('Orange Apple'.split()) == sorted(e_values)


def test_set(e3):
	xpath = 'title'
	e = e3.getOne(xpath)
	e.setValue('Foods')
	assert e.value == 'Foods'


def test_add(e3):
	newEntry = Entry.fromValue('\n')
	e3.add(newEntry)
	newElement = Element.fromString(data="<item>Cake</item>")
	e3.add(newElement)
	e_values = [e.value for e in e3.getAll('item')]
	assert sorted('Orange Apple Cake'.split()) == sorted(e_values)


def test_add_2(e3):
	orangeItemIndex = e3.getIndexByValue('item', 'Orange')
	newEntry = Entry.fromValue('\n')
	newElement = Element.fromString(data="<item>Cake</item>")
	newIndex = orangeItemIndex + 1
	e3.addAll([newEntry, newElement], index = newIndex)
	e_values = [e.value for e in e3.getAll('item')]
	assert sorted('Orange Apple Cake'.split()) == sorted(e_values)
	assert e_values.index('Orange') == 0
	assert e_values.index('Cake') == 1


def test_delete(e3):
	orangeItem = e3.getOneByValue('item', 'Orange')
	entry = orangeItem.nextSibling
	e3.detachAll([orangeItem, entry])
	e_values = [e.value for e in e3.get('item')]
	assert e_values == ['Apple']
	

def test_delete_2(e3):
	orangeItem = e3.getOneByValue('item', 'Orange')
	entry = orangeItem.prevSibling
	e3.detachAll([orangeItem, entry])
	e_values = [e.value for e in e3.get('item')]
	assert e_values == ['Apple']


def test_prevSibling(e3):
	appleItem = e3.getOneByValue('item', 'Apple')
	entry = appleItem.prevSibling
	assert entry.data == '\n'
	orangeItem = entry.prevSibling
	assert orangeItem.value == 'Orange'


def test_nextSibling(e3):
	appleItem = e3.getOneByValue('item', 'Apple')
	entry = appleItem.nextSibling
	assert entry.data == '\n'
	with pytest.raises(KeyError):
		entry.nextSibling




### SECTION
# Basic xpath checks


def test_xpath_1(e1):
	xpath = 'title'
	e = e1.get(xpath)[0]
	assert e.value == 'Fruit'


def test_xpath_2(e1):
	xpath = 'item'
	e_list = e1.get(xpath)
	assert len(e_list) == 3
	e_values = sorted([e.value for e in e_list])
	assert e_values == sorted('Orange Apple Cake'.split())


def test_xpath_3(e1):
	xpath = 'sublist/title'
	e = e1.get(xpath)[0]
	assert e.value == 'Planets'


def test_xpath_4(e1):
	xpath = 'sublist/planet'
	e_list = e1.get(xpath)
	assert len(e_list) == 4
	e_texts = sorted([e.text for e in e_list])
	assert e_texts == sorted('1 2 3 4'.split())


def test_xpath_5(e1):
	xpath = 'sublist/planet/name'
	e_list = e1.get(xpath)
	assert len(e_list) == 4
	e_values = sorted([e.value for e in e_list])
	assert e_values == sorted('Mercury Venus Earth Mars'.split())


def test_xpath_6(e1):
	xpath = '//name'
	e_list = e1.get(xpath)
	assert len(e_list) == 4
	e_values = sorted([e.value for e in e_list])
	assert e_values == sorted('Mercury Venus Earth Mars'.split())


def test_xpath_7(e1):
	xpath = "sublist[@title='Planets']"
	e_list = e1.get(xpath)
	assert len(e_list) == 1
	e = e_list[0]
	assert e.name == 'sublist'
	assert e.getValue('title') == 'Planets'


def test_xpath_8(e1):
	xpath = "languages/language[@category='Python']"
	e_list = e1.get(xpath)
	assert len(e_list) == 2
	versions = [e.getValue('version') for e in e_list]
	assert sorted(versions) == ['2','3']


def test_xpath_9(e1):
	xpath = "languages/language[@category='Python'][@version='2']"
	e_list = e1.get(xpath)
	assert len(e_list) == 1
	versions = [e.getValue('version') for e in e_list]
	assert sorted(versions) == ['2']




### SECTION
# Property tests


def test_entryData(e2):
	xpath = 'bar'
	assert e2.get(xpath)[0].entryData == 'mars'


def test_value(e2):
	xpath = 'bar/bas'
	assert e2.get(xpath)[0].value == 'ASD'


def test_value2(e2):
	xpath = 'bar/bas'
	assert e2.getOne(xpath).value == 'ASD'


def basicTests():
	# blank
	e = Element()
	# from text
	text2 = "<hello>world</hello>"
	e2 = Element.fromString(data=text2)
	print e2.hello
	# with logger
	text3 = "<foo>hello<bar>mars</bar></foo>"
	e3 = Element.fromString(data=text3, loggers=[logger])
	print e3.foo.bar




if __name__ == '__main__':
	main()

