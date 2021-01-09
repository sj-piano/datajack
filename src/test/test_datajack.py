from .. import code
Datajack = code.Datajack.Datajack
Element = code.Element.Element
Entry = code.Element.Entry
import unittest




class TestBasic(unittest.TestCase):


	@classmethod
	def setUpClass(klass):
		klass.d = Datajack()
	

	def test_hello(self):
		self.assertEqual(self.d.hello(), 'world')




class TestExampleHello(unittest.TestCase):


	@classmethod
	def setUpClass(klass):
		with open('src/data/hello.txt') as f:
			data = f.read()
			klass.data = data
			klass.d = Datajack(data)


	def test_getElementValue(self):
		self.assertEqual(self.d.root.value, 'world')




class TestCRUDFunctionality(unittest.TestCase):


	@classmethod
	def setUpClass(klass):
		with open('src/data/test1.txt') as f:
			data = f.read()
			klass.data = data
			klass.d = Datajack(data)
	

	def test_getValue(self):
		d = self.d
		xpath = 'sublist/title'
		e = d.getOne(xpath)
		self.assertEqual(e.value, 'Planets')
	
	
	def test_getValue2(self):
		d = self.d
		xpath = 'sublist/@planet'
		e = d.getOneByEntryData(xpath, '3')
		e2 = e.getOne('name')
		self.assertEqual(e2.value, 'Earth')


	def test_setValue(self):
		d = Datajack(self.data)
		xpath = '//@name'
		nameItems = d.getAll(xpath)
		marsNameItem = [x for x in nameItems if x.value == 'Mars'][0]
		self.assertEqual(marsNameItem.parent.name, 'planet')
		marsNameItem.setValue('Sol_4')
		xpath = 'sublist/@planet/name'
		names = [x.value for x in d.get(xpath)]
		expectedNames = 'Mercury Venus Earth Sol_4'.split()
		self.assertEqual(sorted(expectedNames), sorted(names))


	def test_delete(self):
		d = Datajack(self.data)
		xpath = 'sublist/@planet'
		e = d.getOneByEntryData(xpath, '3')
		e2 = e.nextSibling
		d.detachAll([e, e2])
		xpath = 'sublist/@planet/name'
		names = [x.value for x in d.get(xpath)]
		expectedNames = 'Mercury Venus Mars'.split()
		self.assertEqual(sorted(expectedNames), sorted(names))


	def test_add(self):
		d = Datajack(self.data)
		xpath = 'sublist'
		e = d.getOne(xpath)
		planet = Element.fromString(data='<planet>5<name>Jupiter</name></planet>')
		entry = Entry.fromValue('\n')
		e.addAll([planet, entry])
		xpath = 'sublist/@planet/name'
		names = [x.value for x in d.get(xpath)]
		self.assertEqual(names[4], 'Jupiter')



class TestFile(unittest.TestCase):


	@classmethod
	def setUpClass(klass):
		klass.filePath1 = 'src/data/hello.txt'
		klass.filePath2 = 'src/data/test1.txt'
		klass.filePath3 = 'src/data/test1_output.txt'
	

	def test_getValue(self):
		d = Datajack.fromFile(self.filePath2)
		xpath = 'sublist/title'
		e = d.getOne(xpath)
		self.assertEqual(e.value, 'Planets')
	

	def test_setValue(self):
		d = Datajack.fromFile(self.filePath2)
		xpath = 'sublist/@planet/name'
		nameItems = d.getAll(xpath)
		self.assertEqual(nameItems[3].value, 'Mars')
		nameItems[3].setValue('Sol_4')
		d.writeToFile(self.filePath3)
		d2 = Datajack.fromFile(self.filePath3)
		xpath = 'sublist/@planet/name'
		nameItems = d2.getAll(xpath)
		self.assertEqual(nameItems[3].value, 'Sol_4')
	



if __name__ == '__main__':
	unittest.main()
