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
		xpath = "sublist/title"
		e = d.getOne(xpath)
		self.assertEqual(e.value, 'Planets')
	
	
	def test_getValue2(self):
		d = self.d
		xpath = 'sublist/@planet'
		e = d.getOneByEntryData(xpath, '3')
		e2 = e.getOne('name')
		self.assertEqual(e2.value, 'Earth')






if __name__ == '__main__':
	unittest.main()
