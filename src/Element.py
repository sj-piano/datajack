#!/usr/bin/python


import util
import logging


# IMMUTABLE DATA
elementNameCharacters = "0123456789abcdefghijklmnopqrstuvwxyz_-."
entryCharacters = "!#$%&'()*+,-./0123456789:;=?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[]^_`abcdefghijklmnopqrstuvwxyz{|}~"
entryCharacters += "\""
escapedCharacters = "<>\\"
whitespaceCharacters = " \t\n"
entryCharacters += escapedCharacters + whitespaceCharacters
# END IMMUTABLE DATA



def main():

	basicTests()


def basicTests():
	# blank
	e = Element()
	# from text
	text2 = "<hello>world</hello>"
	e2 = Element.fromString(data=text2)
	print e2.hello
	# with logger
	text3 = "<foo>hello<bar>mars</bar></foo>"
	logger = util.createLogger({'name':'element','level':'debug'})
	e3 = Element.fromString(data=text3, loggers=[logger])
	print e3.foo.bar




class Element:
	"""EML object"""

	
	def __init__(self):
		self.name = ""
		self.endName = ""
		self.complete = False
		self.children = []
		self.parent = None
		self.logger = None
		# dataIndex, lineNumber, and lineIndex exist with reference to the original data (which includes escape characters). They record the location of the start of an element.
		self.dataIndex = 0
		self.lineNumber = 0
		self.lineIndex = 0
	
	
	def hello(self):
		return "world"
	

	@classmethod
	def fromString(self, *args, **kwargs):
		util.confirmNoArgs(args)
		required = 'data:s'
		data = util.getRequiredKeys(kwargs, required)
		logger, log, deb = util.loadOrCreateLogger(kwargs, 'element')
		e = Element()
		# process data into an Element tree.
		parameters = util.DotDict(kwargs)
		parameters.dataLength = len(data)
		parameters.dataIndex = 0
		log("Begin parsing data into an Element tree.")
		deb("Data: " + data)
		e.processString(**parameters)
		log("Element parsed. Name = '{name}'. Children = {c}.".format(name=e.name, c=e.nc))
		return e


	def processString(self, *args, **kwargs):
		# This is a recursive function. It will be called on the next Element that we find.
		# Notes:
		# - An Element can contain 0 items, where an item is an Element or an Entry.
		# Examples: 
		# - In <hello>world</hello>, the element "hello" contains the entry "world".
		# - In <a><b>foo</b>bar</a>, the element "a" contains the element "b" and the entry "bar". The element "b" contains the entry "foo".
		# Notes:
		# - An entry consists of at least one printable ASCII byte.
		# - An element consists of two identical tags, each enclosed in angle brackets. The end tag contains an extra forward slash.
		# - Valid tag names can contain these characters: lower-case letters from a-z, underscore, hyphen, period, digits 0-9.
		# - As we proceed through the data, we will encounter characters in several contexts: 
		# -- empty (we haven't started yet, or we've just finished an Element or Entry)
		# -- tagOpen (we've just opened a tag, but we don't yet know if it's a startTag or an endTag)
		# -- startTagName (we're within the tagName of a startTag)
		# -- startTagClose (we've just closed a startTag)
		# -- endTagOpen, endTagClose, endTagName
		# - Approach: As we encounter each character, we interpret it based on the current context.
		util.confirmNoArgs(args)
		required = 'data:s, dataLength:i, dataIndex:i'
		data, dataLength, dataIndex = util.getRequiredKeys(kwargs, required)
		self.dataIndex = dataIndex
		optional = 'parent, lineNumber:i, lineIndex:i'
		defaults = (None, 0, 0)
		parent, lineNumber, lineIndex = util.getOptionalKeys(kwargs, optional, defaults)
		parameters = util.DotDict(kwargs)
		self.parent = parent
		self.lineNumber = lineNumber
		self.lineIndex = lineIndex
		logger, log, deb = util.loadOrCreateLogger(kwargs, 'element')
		self.logger = logger
		if self.parent is not None:
			deb("Switch to Element")
		statusMsg = "Element: context [{c}], byte [{b}], dataIndex [{di}], lineNumber [{ln}], lineIndex [{li}]."
		context = "empty"
		# we test for (byte + context) combination that we're interested in, and raise an Error if we get any other combination.
		success = False # have we successfully interpreted the current byte?
		while True:
			
			try:
				byte = data[dataIndex]
			except IndexError as e:
				statusMsg = statusMsg.format(c=context, b=byte, di=dataIndex, ln=lineNumber, li=lineIndex)
				statusMsg += " No more data left, but Element is not complete."
				raise Exception(statusMsg)
			
			if byte == "\n": # we've moved to a new line.
				lineIndex = 0
				lineNumber += 1
			
			deb(statusMsg.format(c=context, b=byte, di=dataIndex, ln=lineNumber, li=lineIndex))
			
			if byte == "<":
				if context == "empty":
					context = "tagOpen"
					success = True
				elif context == "startTagClose":
					context = "tagOpen"
					success = True
			elif byte == ">":
				if context == "startTagName":
					context = "startTagClose"
					success = True
				elif context == "endTagName":
					context = "endTagClose"
					# we've arrived at the end of this Element.
					if self.name != self.endName:
						statusMsg = statusMsg.format(c=context, b=byte, di=dataIndex, ln=lineNumber, li=lineIndex)
						statusMsg += " Finished building Element, but endTagName ({e}) is not the same as startTagName ({s}).".format(e=self.endName, s=self.name)
						raise Exception(statusMsg)
					self.complete = True
					if self.parent is not None:
						deb("Element parsed. Name = '{name}'. Children = {c}.".format(name=self.name, c=len(self.children)))
					break

			elif byte == "/":
				if context == "tagOpen":
					context = "endTagOpen"
					success = True
				elif context == "startTagClose":
					deb("Switch to Entry.")
					parameters.dataIndex = dataIndex
					parameters.lineNumber = lineNumber
					parameters.lineIndex = lineIndex
					parameters.parent = self
					entry, dataIndex, lineNumber, lineIndex = Entry.fromString(**parameters)
					self.children.append(entry)
					context = "empty"
					success = True
			elif byte in elementNameCharacters:
				if context == "tagOpen":
					context = "startTagName"
					self.name += byte
					success = True
				elif context == "startTagName":
					self.name += byte
					success = True
				elif context == "startTagClose":
					deb("Switch to Entry.")
					parameters.dataIndex = dataIndex
					parameters.lineNumber = lineNumber
					parameters.lineIndex = lineIndex
					parameters.parent = self
					entry, dataIndex, lineNumber, lineIndex = Entry.fromString(**parameters)
					self.children.append(entry)
					context = "empty"
					success = True
				elif context == "endTagOpen":
					context = "endTagName"
					self.endName += byte
					success = True
				elif context == "endTagName":
					self.endName += byte
					success = True

			elif byte in entryCharacters:
				if context == "startTagClose":
					deb("Switch to Entry.")
					parameters.dataIndex = dataIndex
					parameters.lineNumber = lineNumber
					parameters.lineIndex = lineIndex
					parameters.parent = self
					entry, dataIndex, lineNumber, lineIndex = Entry.fromString(**parameters)
					self.children.append(entry)
					context = "empty"
					success = True


			if not success:
				statusMsg = statusMsg.format(c=context, b=byte, di=dataIndex, ln=lineNumber, li=lineIndex)
				statusMsg += " Byte not successfully interpreted."
				raise Exception(statusMsg)
			success = False
			dataIndex += 1
			lineIndex += 1
		
		
		if self.parent is None:
			# This is the root Element of the data.
			# If there is any data left over, this is an error.
			if dataIndex < dataLength - 1:
				remainingData = data[dataIndex+1:]
				msg = "Finished building root element, but there is remaining data: {}".format(repr(remainingData))
				raise ValueError(msg)
		return self


	def get(self, xpath):
		if '/' in xpath:
			raise ValueError
		if xpath in self.children:
			return self.children[xpath]
		raise ValueError






def stop(msg=None):
	if msg: print "\n%s\n" % msg
	import sys; sys.exit()


if __name__ == "__main__":
	main()
