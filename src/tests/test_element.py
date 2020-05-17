import unittest
from src import Element
from src.util.createLogger import createLogger



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
		loggerSettings = {'name': 'element', 'level': 'info'}
		logger = createLogger(loggerSettings)
		loggers = [logger]
		parameters = {'extraParameter': 123}
		klass.e = Element.fromString(data=data, loggers=loggers, **parameters)
	
	def test_getValue(self):
		self.assertEqual(self.e.value, 'world')




if __name__ == '__main__':
	main()
