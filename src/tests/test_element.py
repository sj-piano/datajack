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




class TestNested(unittest.TestCase):

	@classmethod
	def setUpClass(klass):
		data = "<foo>hello<bar>mars</bar></foo>"
		logger = createLogger({'name': 'element', 'level': 'info'})
		logger.info('Data: ' + data)
		klass.e = Element.fromString(data=data, loggers=[logger])
	
	def test_getValue(self):
		xpath = 'foo/bar'
		self.assertEqual(self.e.get(xpath).first.value, 'mars')




if __name__ == '__main__':
	main()
