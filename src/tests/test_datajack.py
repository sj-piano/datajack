import unittest
from src.datajack import *




class TestDatajack(unittest.TestCase):

	@classmethod
	def setUpClass(klass):
		klass.dj = Datajack()
	
	def test_hello(self):
		self.assertEqual(self.dj.hello(), 'world')




if __name__ == '__main__':
	unittest.main()
