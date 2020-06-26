import unittest
from src import Datajack




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
			klass.d = Datajack(data)
	
	def test_getElementValue(self):
		self.assertEqual(self.d.root.value, 'world')



if __name__ == '__main__':
	unittest.main()
