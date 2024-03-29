from .. import code, util
Element = code.Element.Element
Entry = code.Element.Entry
import unittest




class TestBasic(unittest.TestCase):


  @classmethod
  def setUpClass(klass):
    klass.e = Element()


  def test_hello(self):
    self.assertEqual(self.e.hello(), 'world')




class TestExampleHello(unittest.TestCase):


  @classmethod
  def setUpClass(klass):
    data = "<hello>world</hello>"
    parameters = {'extraParameter': 123}
    klass.e = Element.fromString(data=data, **parameters)


  def test_getValue(self):
    self.assertEqual(self.e.value, 'world')




class TestNested(unittest.TestCase):


  @classmethod
  def setUpClass(klass):
    data = "<foo>hello<bar>mars<bas>ASD</bas></bar></foo>"
    klass.e = Element.fromString(data=data)


  def test_getEntryData(self):
    xpath = 'bar'
    self.assertEqual(self.e.get(xpath)[0].entryData, 'mars')


  def test_getValue(self):
    xpath = 'bar/bas'
    self.assertEqual(self.e.get(xpath)[0].value, 'ASD')


  def test_getValue2(self):
    xpath = 'bar/bas'
    self.assertEqual(self.e.getOne(xpath).value, 'ASD')




class TestMultiple(unittest.TestCase):


  @classmethod
  def setUpClass(klass):
    data = """
<list>
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
</list>
"""
    data = data.strip()
    klass.e = Element.fromString(data=data)


  def test_getMultiple(self):
    xpath = "@item"
    itemValues = [x.value for x in self.e.get(xpath)]
    expectedValues = 'Orange Apple Cake'.split()
    self.assertEqual(itemValues, expectedValues)


  def test_getMultiple2(self):
    xpath = "sublist/@planet/name"
    names = [x.value for x in self.e.get(xpath)]
    expectedNames = "Mercury Venus Earth Mars".split()
    self.assertEqual(sorted(expectedNames), sorted(names))


  def test_getMultiple3(self):
    xpath = "//@name"
    names = [x.value for x in self.e.get(xpath)]
    expectedNames = "Mercury Venus Earth Mars".split()
    self.assertEqual(sorted(expectedNames), sorted(names))


  def test_getMultipleError(self):
    xpath = "//@planet"
    with self.assertRaises(ValueError):
      self.e.getOne(xpath)


  def test_getAll(self):
    xpath = "//@planet"
    entryDataValues = [x.entryData for x in self.e.getAll(xpath)]
    expectedValues = "1 2 3 4".split()
    self.assertEqual(sorted(expectedValues), sorted(entryDataValues))


  def test_getAllError(self):
    xpath = "//@planetFOO"
    with self.assertRaises(ValueError):
      entryDataValues = [x.entryData for x in self.e.getAll(xpath)]




class CRUDFunctionality(unittest.TestCase):


  @classmethod
  def setUpClass(klass):
    data = """
<list>
<title>Fruit</title>
<item>Orange</item>
<item>Apple</item>
</list>
"""
    data = data.strip()
    klass.data = data
    klass.e = Element.fromString(data=data)


  def test_get(self):
    xpath = 'title'
    x = self.e.getOne(xpath)
    self.assertEquals(x.value, 'Fruit')


  def test_get2(self):
    xpath = '@item'
    x = self.e.getAll(xpath)
    y = x[0]
    self.assertEquals(y.value, 'Orange')


  def test_set(self):
    e = Element.fromString(data=self.e.data)
    xpath = 'title'
    x = e.getOne(xpath)
    x.setValue('Foods')
    self.assertEquals(x.value, 'Foods')


  def test_add(self):
    e = Element.fromString(data=self.e.data)
    newEntry = Entry.fromValue('\n')
    e.add(newEntry)
    newElement = Element.fromString(data="<item>Cake</item>")
    e.add(newElement)
    items = e.getAll('@item')
    self.assertEquals(items[2].value, 'Cake')


  def test_add2(self):
    e = Element.fromString(data=self.e.data)
    orangeItemIndex = e.getIndexByValue('@item', 'Orange')
    newEntry = Entry.fromValue('\n')
    newElement = Element.fromString(data="<item>Cake</item>")
    e.addAll([newEntry, newElement], index = orangeItemIndex + 1)
    items = e.getAll('@item')
    self.assertEquals(items[1].value, 'Cake')


  def test_delete(self):
    e = Element.fromString(data=self.e.data)
    orangeItem = e.getOneByValue('@item', 'Orange')
    entry = orangeItem.nextSibling
    e.detachAll([orangeItem, entry])
    itemValues = [x.value for x in e.get('@item')]
    self.assertEqual(itemValues, ['Apple'])


  def test_delete2(self):
    e = Element.fromString(data=self.e.data)
    orangeItem = e.getOneByValue('@item', 'Orange')
    entry = orangeItem.prevSibling
    e.detachAll([orangeItem, entry])
    itemValues = [x.value for x in e.get('@item')]
    self.assertEqual(itemValues, ['Apple'])


  def test_prevSibling(self):
    e = Element.fromString(data=self.e.data)
    appleItem = e.getOneByValue('@item', 'Apple')
    entry = appleItem.prevSibling
    self.assertEqual(entry.data, '\n')
    orangeItem = entry.prevSibling
    self.assertEqual(orangeItem.value, 'Orange')


  def test_nextSibling(self):
    e = Element.fromString(data=self.e.data)
    appleItem = e.getOneByValue('@item', 'Apple')
    entry = appleItem.nextSibling
    self.assertEqual(entry.data, '\n')
    with self.assertRaises(KeyError):
      newItem = entry.nextSibling








if __name__ == '__main__':
  main()
