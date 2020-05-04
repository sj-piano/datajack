#!/usr/bin/python


from utils.createLogger import createLogger
import logging


def main():

	basicTests()


def basicTests():
	# blank
	e = Element()
	# from text
	text2 = "<hello>world</hello>"
	e2 = Element.fromString(text2)
	print e2.world
	# with logger
	text3 = "<foo>hello<bar>mars</bar></foo>"
	logger = createLogger({'name':'element','level':'debug'})
	e3 = Element.fromString(text3, logger)




class Element:
	"""EML object"""

	
	def __init__(self):
		self.name = ""
		self.endName = ""
		self.complete = False
		self.children = []
		self.parent = None
		self.logger = None
		# line and offset exist with reference to the original data (which includes escape characters).
		self.line = None
		self.offset = None
	

	@classmethod
	def fromString(klass, text, logger=None):
		if not isinstance(text, str):
			raise TypeError()
		if logger == None:
			logger = createNullLogger()
		e = klass() # e = element
		e.logger = logger
		e.line = 0
		e.offset = 0
		e.processString(text)
		e.logger.info("Element parsed. Name = '{}'".format(e.name))
		return e
	

	def processString(self, text):
		# This method should be run only once for a given element instance, at its creation from a string.
		pass

		




def createNullLogger():
	logger = logging.getLogger(__name__)
	handler = logging.NullHandler()
	logger.addHandler(handler)
	return logger



if __name__ == "__main__":
	main()
