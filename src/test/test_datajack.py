# The tests are run in the 'datajack' package directory,
# so the import paths start from there.
import unittest
from src.code.Datajack import Datajack




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




class Test1(unittest.TestCase):


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




if __name__ == '__main__':
	unittest.main()
