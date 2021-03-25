# Imports
import pytest
import argparse
import logging
import pkgutil




# Relative imports
from .. import code
from .. import util




# Shortcuts
NS = argparse.Namespace
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
# -- pytest -o log_cli=true --log-cli-level=INFO --log-format="%(levelname)s [%(lineno)s: %(funcName)s] %(message)s" src/test/test_element.py::test_hello
# -- This is very useful when you want to manually check the operation of the functions during the test.








### SECTION
# Basic checks.


def test_hello():
  e = Element()
  assert e.hello() == 'world'


def test_hello_2():
  d = "<hello>world</hello>"
  e = Element.from_string(data=d)
  assert e.text == 'world'








### SECTION
# Data fixtures


@pytest.fixture(scope="module")
def e1():
  d_file = '../data/test1.txt'
  d = pkgutil.get_data(__name__, d_file)
  e1 = Element.from_string(data=d.strip())
  yield e1


@pytest.fixture(scope="module")
def e2():
  d = """
<foo>hello
<bar>mars<bas>ASD</bas></bar>
</foo>
"""
  e2 = Element.from_string(data=d.strip())
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
  e3 = Element.from_string(data=d.strip())
  yield e3


@pytest.fixture(scope="function")
def e4():
  d_file = '../data/hello.txt'
  d = pkgutil.get_data(__name__, d_file)
  e4 = Element.from_string(data=d.strip())
  yield e4








### SECTION
# More basic checks.


def test_hello_3(e4):
  assert e4.text == 'world'








### SECTION
# CRUD tests


def test_get(e3):
  xpath = 'title'
  e = e3.get_one(xpath)
  assert e.value == 'Fruit'


def test_get_2(e3):
  xpath = 'item'
  e_values = [e.value for e in e3.get_all(xpath)]
  assert sorted('Orange Apple'.split()) == sorted(e_values)


def test_set(e3):
  xpath = 'title'
  e = e3.get_one(xpath)
  e.set_value('Foods')
  assert e.value == 'Foods'


def test_add(e3):
  new_entry = Entry.from_value('\n')
  e3.add(new_entry)
  new_element = Element.from_string(data="<item>Cake</item>")
  e3.add(new_element)
  e_values = [e.value for e in e3.get_all('item')]
  assert sorted('Orange Apple Cake'.split()) == sorted(e_values)


def test_add_2(e3):
  orange_item_index = e3.get_index_by_value('item', 'Orange')
  new_entry = Entry.from_value('\n')
  new_element = Element.from_string(data="<item>Cake</item>")
  new_index = orange_item_index + 1
  e3.add_all([new_entry, new_element], index = new_index)
  e_values = [e.value for e in e3.get_all('item')]
  assert sorted('Orange Apple Cake'.split()) == sorted(e_values)
  assert e_values.index('Orange') == 0
  assert e_values.index('Cake') == 1


def test_delete(e3):
  orange_item = e3.get_one_by_value('item', 'Orange')
  entry = orange_item.next_sibling
  e3.detach_all([orange_item, entry])
  e_values = [e.value for e in e3.get('item')]
  assert e_values == ['Apple']


def test_delete_2(e3):
  orange_item = e3.get_one_by_value('item', 'Orange')
  entry = orange_item.prev_sibling
  e3.detach_all([orange_item, entry])
  e_values = [e.value for e in e3.get('item')]
  assert e_values == ['Apple']


def test_prev_sibling(e3):
  apple_item = e3.get_one_by_value('item', 'Apple')
  entry = apple_item.prev_sibling
  assert entry.data == '\n'
  orange_item = entry.prev_sibling
  assert orange_item.value == 'Orange'


def test_next_sibling(e3):
  apple_item = e3.get_one_by_value('item', 'Apple')
  entry = apple_item.next_sibling
  assert entry.data == '\n'
  with pytest.raises(KeyError):
    entry.next_sibling








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
  assert e.get_value('title') == 'Planets'


def test_xpath_8(e1):
  xpath = "languages/language[@category='Python']"
  e_list = e1.get(xpath)
  assert len(e_list) == 2
  versions = [e.get_value('version') for e in e_list]
  assert sorted(versions) == ['2','3']


def test_xpath_9(e1):
  xpath = "languages/language[@category='Python'][@version='2']"
  e_list = e1.get(xpath)
  assert len(e_list) == 1
  versions = [e.get_value('version') for e in e_list]
  assert sorted(versions) == ['2']








### SECTION
# Property tests


def test_entry_data(e2):
  xpath = 'bar'
  assert e2.get(xpath)[0].entry_data == 'mars'


def test_value(e2):
  xpath = 'bar/bas'
  assert e2.get(xpath)[0].value == 'ASD'


def test_value2(e2):
  xpath = 'bar/bas'
  assert e2.get_one(xpath).value == 'ASD'








if __name__ == '__main__':
  main()

