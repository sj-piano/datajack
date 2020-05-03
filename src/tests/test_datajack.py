import unittest
from src import Datajack




class TestDatajack(unittest.TestCase):

	@classmethod
	def setUpClass(klass):
		klass.dj = Datajack()
	
	def test_hello(self):
		self.assertEqual(self.dj.hello(), 'world')




class TestExampleHello(unittest.TestCase):

	@classmethod
	def setUpClass(klass):
		klass.dj = Datajack()
		with open('src/data/hello.txt') as f:
			klass.exampleHello = f.read()
	
	def test_value(self):
		self.assertEqual(self.dj.hello, 'world')



if __name__ == '__main__':
	unittest.main()
