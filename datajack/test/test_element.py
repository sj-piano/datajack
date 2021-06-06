# Imports
import pytest
import pkgutil
import json




# Relative imports
from .. import code
from .. import util




# Shortcuts
Element = code.Element.Element
Entry = code.Element.Entry




# Setup for this file.
@pytest.fixture(autouse=True, scope='module')
def setup_module(pytestconfig):
  # If log_level is supplied to pytest in the commandline args, then use it to set up the logging in the application code.
  log_level = pytestconfig.getoption('log_cli_level')
  if log_level is not None:
    log_level = log_level.lower()
    code.setup(log_level = log_level)




# Notes:
# - Running the command { pytest3 } or the command { pytest3 datajack/test/test_element.py }
# in the package directory should load and run the tests in this file.
# - Run a specific test:
# -- pytest3 datajack/test/test_element.py::test_hello
# - Run quietly:
# -- [all tests] pytest3 -q
# -- pytest3 -q datajack/test/test_element.py
# - Print log output in real-time during a single test:
# -- pytest3 -s --log-cli-level=INFO datajack/test/test_element.py::test_hello
# --- Note the use of the pytest -s option. This will cause print statements in the test code itself to also produce output.








# ### SECTION
# Basic checks.


def test_hello():
  e = Element()
  print('mars')
  assert e.hello() == 'world'


def test_hello_2():
  d = "<hello>world</hello>"
  e = Element.from_string(data=d)
  assert e.text == 'world'








# ### SECTION
# Data fixtures


@pytest.fixture(scope="module")
def e1():
  d_file = '../data/test1.txt'
  d = pkgutil.get_data(__name__, d_file).decode('ascii')
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
  d = pkgutil.get_data(__name__, d_file).decode('ascii')
  e4 = Element.from_string(data=d.strip())
  yield e4


@pytest.fixture(scope="function")
def e5():
  d_file = '../data/transaction1.txt'
  d = pkgutil.get_data(__name__, d_file).decode('ascii')
  e5 = Element.from_string(data=d.strip())
  yield e5








# ### SECTION
# More basic checks.


def test_hello_3(e4):
  assert e4.text == 'world'


def test_tx1_1(e5):
  assert len(e5.children) == 11 == e5.nc


def test_tx1_2(e5):
  assert e5.element_child[0].name == 'id'
  assert e5.element_children_names[0] == 'id'


def test_tx1_3(e5):
  assert e5.start_tag == '<transaction>'
  assert e5.end_tag == '</transaction>'







# ### SECTION
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








# ### SECTION
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
  assert sorted(versions) == ['2', '3']


def test_xpath_9(e1):
  xpath = "languages/language[@category='Python'][@version='2']"
  e_list = e1.get(xpath)
  assert len(e_list) == 1
  versions = [e.get_value('version') for e in e_list]
  assert sorted(versions) == ['2']








# ### SECTION
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




# ### SECTION
# Conversion tests


def test_to_dict():
  s = """
<list>
<title>Fruit</title>
<item>Orange</item>
</list>
"""
  e = Element.from_string(data=s.strip())
  d = e.to_dict()
  d_json = json.dumps(d, sort_keys=True)
  expected_json = '{"list": {"item": "Orange", "title": "Fruit"}}'
  assert d_json == expected_json


def test_to_dict_2():
  s = """
<list>
<title>Fruit</title>
<item>Orange</item>
<item>Apple</item>
</list>
"""
  expected = {
    "list": {
      "item": [
        "Orange",
        "Apple"
      ],
      "title": "Fruit"
    }
  }
  e = Element.from_string(data=s.strip())
  d = e.to_dict()
  d_json = json.dumps(d, sort_keys=True)
  expected_json = json.dumps(expected, sort_keys=True)
  assert d_json == expected_json


def test_to_dict_3():
  # Entry data that is _not_ in a leaf element will be ignored.
  s = """
<foo>hello
<bar>mars<bas>ASD</bas></bar>
</foo>
"""
  e = Element.from_string(data=s.strip())
  d = e.to_dict()
  expected = {
    'foo': {
      'bar': {
        'bas': 'ASD'
      }
    }
  }
  expected_json = json.dumps(expected, sort_keys=True)
  d_json = json.dumps(d, sort_keys=True)
  assert d_json == expected_json


def test_from_dict():
  d = {'hello': 'world'}
  e = Element.from_dict(d)
  s = "<hello>world</hello>"
  expected = Element.from_string(s)
  assert e.to_json() == expected.to_json()


def test_from_dict_2():
  d = {
    "hello": {
      "foo": [
        "1",
        "2",
        {
          "b": "a"
        }
      ],
      "bar": "arf"
    }
  }
  e = Element.from_dict(d)
  s = """
<hello>
<foo>1</foo>
<foo>2</foo>
<foo>3<b>a</b></foo>
<bar>arf</bar>
</hello>
"""
  expected = Element.from_string(s.strip())
  assert e.to_json() == expected.to_json()


def test_from_json(e1):
  j = e1.to_json()
  y = Element.from_json(j)
  result, msg = y.matches_tree_of(e1)
  if not result:
    raise ValueError(msg)
  assert result == True


def test_to_json(e5):
  d = {
    "transaction": {
      "fee": {
        "satoshi": "225"
      },
      "id": "1",
      "input": {
        "amount": {
          "bitcoin": "0.00200000"
        },
        "previous_output_index": "9",
        "private_key": " 0000000000000000000000007468655f6c6962726172795f6f665f626162656c ",
        "txid": " 8482e48391425d88fe30bd4066957000335f58e83f854f997146f41b9493b4ce "
      },
      "notes": " http://edgecase.net/articles/bitcoin_transaction_test_set_2 - Transaction 1: 1 input, 1 output ",
      "output": {
        "address": "12RbVkKwHcwHbMZmnSVAyR4g88ZChpQD6f",
        "amount": {
          "bitcoin": "0.00199775"
        }
      }
    }
  }
  expected = json.dumps(d, sort_keys=True)
  j = e5.to_json()
  assert j == expected





