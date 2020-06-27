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




if __name__ == '__main__':
	unittest.main()
