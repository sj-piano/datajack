import unittest
from src import Datajack




class TestBasic(unittest.TestCase):

	@classmethod
	def setUpClass(klass):
		klass.dj = Datajack()
	
	def test_hello(self):
		self.assertEqual(self.dj.hello(), 'world')




class TestExampleHello(unittest.TestCase):

	@classmethod
	def setUpClass(klass):
		with open('src/data/hello.txt') as f:
			data = f.read()
			klass.dj = Datajack(data)
	
	def test_getElementValue(self):
		self.assertEqual(self.dj.get('hello'), 'world')



if __name__ == '__main__':
	unittest.main()
