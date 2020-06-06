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
# define contexts
EMPTY = 0
START_TAG_OPEN = 1
START_TAG_NAME = 2
START_TAG_CLOSE = 3
TAG_OPEN = 4
INSIDE_ELEMENT = 5
END_TAG_OPEN = 6
END_TAG_NAME = 7
END_TAG_CLOSE = 8
DATA = 9
contextNames = {0: 'EMPTY', 1: 'START_TAG_OPEN', 2: 'START_TAG_NAME',
	3: 'START_TAG_CLOSE', 4: 'TAG_OPEN', 5: 'INSIDE_ELEMENT',
	6: 'END_TAG_OPEN', 7: 'END_TAG_NAME', 8: 'END_TAG_CLOSE',
	9: 'DATA'
}
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
		self.finalDataIndex = 0
		self.finalLineNumber = 0
		self.finalLineIndex = 0
	
	
	def hello(self):
		return "world"


	@classmethod
	def fromString(self, *args, **kwargs):
		# both the root element and any child elements are built using this method.
		util.confirmNoArgs(args)
		required = 'data:s'
		data = util.getRequiredItems(kwargs, required)
		optional = 'parent, dataLength:i, dataIndex:i, lineNumber:i, lineIndex:i, recursiveDepth:i'
		defaults = (None, len(data), 0, 0, 0, 0)
		parent, dataLength, dataIndex, lineNumber, lineIndex, recursiveDepth = util.getOptionalItems(kwargs, optional, defaults)
		logger, log, deb = util.loadOrCreateLogger(kwargs, 'element')
		e = Element()
		# process data into an Element tree.
		parameters = util.DotDict(kwargs)
		parameters.parent = parent
		parameters.dataLength = dataLength
		parameters.dataIndex = dataIndex
		parameters.lineNumber = lineNumber
		parameters.lineIndex = lineIndex
		parameters.recursiveDepth = recursiveDepth
		if parent is None:
			log("Begin parsing data into an Element tree.")
		e.processString(**parameters)
		if e.parent is None:
			log("Element parsed. Name = '{name}'. Number of children = {c}.".format(name=e.name, c=e.nc))
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
		# -- empty (we haven't started yet)
		# -- startTagOpen (we've processed the first character, which must be '<')
		# -- startTagName (we're within the tagName of a startTag)
		# -- startTagClose (we've just closed a startTag)
		# -- tagOpen (we've just opened a tag, but we don't yet know if it's this Element's endTag or a child Element's startTag)
		# -- insideElement (we're inside an unfinished Element, and we've just finished a child Element or Entry)
		# -- endTagOpen, endTagName, endTagClose
		# - Approach: As we encounter each character, we interpret it based on the current context.
		util.confirmNoArgs(args)
		required = 'parent, data:s, dataLength:i, dataIndex:i, lineNumber:i, lineIndex:i, recursiveDepth:i'
		parent, data, dataLength, dataIndex, lineNumber, lineIndex, recursiveDepth = util.getRequiredItems(kwargs, required)
		self.parent = parent
		self.dataIndex = dataIndex
		self.lineNumber = lineNumber
		self.lineIndex = lineIndex
		self.recursiveDepth = recursiveDepth
		parameters = util.DotDict(kwargs)
		logger, log, deb = util.loadOrCreateLogger(kwargs, 'element')
		self.logger = logger
		if self.parent is not None:
			deb("Switch to Element")
		statusMsg = "Element: context [{c}], byte [{b}], dataIndex [{di}], lineNumber [{ln}], lineIndex [{li}]."
		# set initial context
		context = EMPTY
		# we test for (byte + context) combination that we're interested in, and raise an Error if we get any other combination.
		success = False # have we successfully interpreted the current byte?
		while True:
			
			try:
				byte = data[dataIndex]
			except IndexError as e:
				statusMsg = statusMsg.format(c=contextNames[context], b=repr(byte), di=dataIndex, ln=lineNumber, li=lineIndex)
				statusMsg += " No more data left, but Element is not complete."
				raise Exception(statusMsg)
			
			if byte == "\n": # we've moved to a new line.
				lineIndex = 0
				lineNumber += 1
			
			deb(statusMsg.format(c=contextNames[context], b=repr(byte), di=dataIndex, ln=lineNumber, li=lineIndex))
			
			if byte == "<":
				if context == EMPTY:
					context = START_TAG_OPEN
					success = True
				elif context == START_TAG_CLOSE:
					context = TAG_OPEN
					success = True
				elif context == INSIDE_ELEMENT:
					context = TAG_OPEN
					success = True
			
			elif byte == ">":
				if context == START_TAG_NAME:
					context = START_TAG_CLOSE
					success = True
				elif context == END_TAG_NAME:
					context = END_TAG_CLOSE
					# we've arrived at the end of this Element.
					if self.name != self.endName:
						statusMsg = statusMsg.format(c=contextNames[context], b=repr(byte), di=dataIndex, ln=lineNumber, li=lineIndex)
						statusMsg += " Finished building Element, but endTagName ({e}) is not the same as startTagName ({s}).".format(e=self.endName, s=self.name)
						raise Exception(statusMsg)
					self.finalDataIndex = dataIndex
					self.finalLineNumber = lineNumber
					self.finalLineIndex = lineIndex
					self.complete = True
					if self.parent is not None:
						deb("Element parsed. Name = '{name}'. Number of children = {c}.".format(name=self.name, c=len(self.children)))
					break

			elif byte == "/":
				if context == TAG_OPEN:
					context = END_TAG_OPEN
					success = True
				elif context == START_TAG_CLOSE:
					deb("Switch to Entry.")
					parameters.dataIndex = dataIndex
					parameters.lineNumber = lineNumber
					parameters.lineIndex = lineIndex
					parameters.parent = self
					entry, dataIndex, lineNumber, lineIndex = Entry.fromString(**parameters)
					self.children.append(entry)
					context = INSIDE_ELEMENT
					success = True
			elif byte in elementNameCharacters:
				if context == START_TAG_OPEN:
					context = START_TAG_NAME
					self.name += byte
					success = True
				elif context == START_TAG_NAME:
					self.name += byte
					success = True
				elif context == START_TAG_CLOSE:
					deb("Switch to Entry.")
					parameters.dataIndex = dataIndex
					parameters.lineNumber = lineNumber
					parameters.lineIndex = lineIndex
					parameters.parent = self
					entry, dataIndex, lineNumber, lineIndex = Entry.fromString(**parameters)
					self.children.append(entry)
					context = INSIDE_ELEMENT
					success = True
				elif context == END_TAG_OPEN:
					context = END_TAG_NAME
					self.endName += byte
					success = True
				elif context == END_TAG_NAME:
					self.endName += byte
					success = True
				elif context == TAG_OPEN:
					deb("Switch to child Element.")
					dataIndex, lineNumber, lineIndex = self.rewindBytes(1, dataIndex, lineNumber, lineIndex)
					parameters.dataIndex = dataIndex
					parameters.lineNumber = lineNumber
					parameters.lineIndex = lineIndex
					parameters.parent = self
					parameters.recursiveDepth = self.recursiveDepth + 1
					child = Element.fromString(**parameters)
					self.children.append(child)
					dataIndex = child.finalDataIndex
					lineNumber = child.finalLineNumber
					lineIndex = child.finalLineIndex
					context = INSIDE_ELEMENT
					success = True

			elif byte in entryCharacters:
				if context == START_TAG_CLOSE:
					deb("Switch to Entry.")
					parameters.dataIndex = dataIndex
					parameters.lineNumber = lineNumber
					parameters.lineIndex = lineIndex
					parameters.parent = self
					entry, dataIndex, lineNumber, lineIndex = Entry.fromString(**parameters)
					self.children.append(entry)
					context = INSIDE_ELEMENT
					success = True

			elif byte in whitespaceCharacters:
				if context == INSIDE_ELEMENT:
					pass


			if not success:
				statusMsg = statusMsg.format(c=contextNames[context], b=repr(byte), di=dataIndex, ln=lineNumber, li=lineIndex)
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

	def rewindBytes(self, nBytes, dataIndex, lineNumber, lineIndex):
		# this doesn't handle newline bytes.
		for i in xrange(nBytes):
			dataIndex -= 1
			lineIndex -= 1
		return dataIndex, lineNumber, lineIndex 
	
	def __str__(self):
		return "Element: [{}]".format(self.name)

	def __iter__(self):
		for child in self.children:
			yield child
	
	@property
	def elementChildren(self):
		for child in self:
			if child.className == "Element":
				yield child
	
	@property
	def entryChildren(self):
		for child in self:
			if child.className == "Entry":
				yield child

	@property
	def startTag(self):
		return "<" + self.name + ">"

	@property
	def endTag(self):
		return "</" + self.endName + ">"

	@property
	def nc(self):
		# calculate number of children.
		return len(self.children)

	@property
	def className(self):
		return self.__class__.__name__

	@property
	def child(self):
		return self.children

	@property
	def tree(self):
		return "\n".join(self.treeLines())

	def treeLines(self):
		if self.parent is None:
			treeLines = ["Tree for " + str(self)]
		else:
			treeLines = [" " + str(self)]
		for child in self:
			childLines = child.treeLines()
			childLines = [("-" + x) for x in childLines]
			treeLines.extend(childLines)
		return treeLines

	@property
	def value(self):
		# this is leaf Elements only.
		# get the value of the entry, delete any whitespace, and return it.
		if not (self.nc == 1 and self.child[0].className == "Entry"):
			raise ValueError("This method requires exactly 1 child that is an Entry.")
		return self.deleteWhitespace(self.child[0].data)

	@staticmethod
	def deleteWhitespace(s):
		return s.translate(None, whitespaceCharacters)
	
	@property
	def entryData(self):
		data = ''
		for child in self.entryChildren:
			data += child.data
		return data

# example tree:
# <article>
# <title>James_Sullivan_on_the_nature_of_banks</title>
# <author_name>stjohn_piano</author_name>
# <date>2017-07-21</date>
# <signed_by_author>no</signed_by_author>
# <content>
# hello world
# <list>
# <title>Guild_Members</title>
# <name>StJohn_Piano</name>
# <name>Robert_Smith</name>
# <name>John_Smith</name>
# <location>Cambridge</location>
# </list>
# <link>
# <type>asset</type>
# <filename>pkgconf-0.8.9.tar.bz2.asc</filename>
# <text>pkgconf-0.8.9.tar.bz2.asc</text>
# <sha256>d9a497da682c7c0990361bbdc9b7c5c961250ec4679e3feda19cfbec37695100</sha256>
# </link>
# <link>
# <type>asset</type>
# <filename>rotor-db-configure-fix.patch.asc</filename>
# <text>rotor-db-configure-fix.patch.asc</text>
# <sha256>bb8cfec3eceeb73e5994cc100a4106a85670a6cab3a622697c91d4c2f9ff083a</sha256>
# </link>
# <link>
# <type>asset</type>
# <filename>rotor.tar.gz.asc</filename>
# <text>rotor.tar.gz.asc</text>
# <sha256>c988aaa62000cfc0858f8526d8ffcd96d497e39b9f1e8b5d9d08ee1575813425</sha256>
# </link>
# </content>
# </article>

	# possible xpaths:
	# 1) title (the title element that is a direct child of the root 'article' element)
	# 2) content/list/title (the title element that is a particular descendant of the root article element)

	# notes:
	# - if xpath specifies multiple results, return list, even if only 1 result is found.
	# - if xpath specifies one result, return a single item, not a list.

	def get(self, xpath):
		if '/' not in xpath:
			name = xpath
			result = self.getElementChildrenWithName(name)
			if len(result) != 1:
				raise ValueError("xpath {x} specified 1 child, but {n} found.".format(x=xpath, n=len(result)))
			return result[0]
		else:
			sections = xpath.split('/')
			name = sections[0]
			restOfPath = '/'.join(sections[1:])
			result1 = self.getElementChildrenWithName(name)
			result2 = []
			for child in result1:
				result3 = child.get(restOfPath)
				result2.append(result3)
			if len(result2) != 1:
				raise ValueError("xpath {x} specified 1 child, but {n} found.".format(x=xpath, n=len(result2)))
			return result2[0]

			
		raise Exception("Shouldn't arrive at the end of this function.")

	def getElementChildrenWithName(self, name):
		result = []
		for child in self.elementChildren:
			if child.name == name:
				result.append(child)
		return result





class Entry:


	def __init__(self):
		self.data = "" # this contains the actual data in bytes of the Entry (after escape characters have been removed)
		self.parent = None
		self.logger = None
		# dataIndex, lineNumber, and lineIndex exist with reference to the original data (which includes escape characters). They record the location of the start of an entry.
		self.dataIndex = 0
		self.lineNumber = 0
		self.lineIndex = 0
		
	
	
	@classmethod
	def fromString(self, *args, **kwargs):
		util.confirmNoArgs(args)
		logger, log, deb = util.loadOrCreateLogger(kwargs, 'element')
		entry = Entry()
		# process data into an Entry.
		dataIndex, lineNumber, lineIndex = entry.processString(**kwargs)
		nBytes = len(entry.data)
		z = 10 # how much of the entry's start/end data to show in the log.
		value = entry.data
		if nBytes > 2 * z:
			value = value[:z] + "..." + value[-z:]
		deb("Entry parsed. Length = {n} bytes. Value = '{v}'.".format(n=nBytes, v=value))
		return entry, dataIndex, lineNumber, lineIndex


	def processString(self, *args, **kwargs):
		# Notes:
		# - An entry consists of at least one printable ASCII byte.
		util.confirmNoArgs(args)
		required = 'data:s, dataLength:i, dataIndex:i, lineNumber:i, lineIndex:i, parent'
		data, dataLength, dataIndex, lineNumber, lineIndex, parent = util.getRequiredItems(kwargs, required)
		self.dataIndex = dataIndex
		self.lineNumber = lineNumber
		self.lineIndex = lineIndex
		self.parent = parent
		logger, log, deb = util.loadOrCreateLogger(kwargs, 'element')
		self.logger = logger
		statusMsg = "Entry: context [{c}], byte [{b}], dataIndex [{di}], lineNumber [{ln}], lineIndex [{li}]."
		context = DATA
		# we test for (byte + context) combination that we're interested in, and raise an Error if we get any other combination.
		success = False # have we successfully interpreted the current byte?
		while True:
			
			try:
				byte = data[dataIndex]
			except IndexError as e:
				statusMsg = statusMsg.format(c=contextNames[context], b=repr(byte), di=dataIndex, ln=lineNumber, li=lineIndex)
				statusMsg += " No more data left, but Element is not complete."
				raise Exception(statusMsg)

			if byte == "\n": # we've moved to a new line.
				lineIndex = 0
				lineNumber += 1

			deb(statusMsg.format(c=contextNames[context], b=repr(byte), di=dataIndex, ln=lineNumber, li=lineIndex))

			if byte == "<":
				if context == DATA:
					# we've encountered a new Element.
					# rewind one byte so that the Element processing loop completes and begins again on this current byte.
					dataIndex, lineNumber, lineIndex = self.rewindOneByte(dataIndex, lineNumber, lineIndex)
					break
			elif byte == ">":
				pass
			elif byte == "\\":
				pass
			elif byte in entryCharacters:
				if context == DATA:
					self.data += byte
					success = True


			if not success:
				statusMsg = statusMsg.format(c=contextNames[context], b=repr(byte), di=dataIndex, ln=lineNumber, li=lineIndex)
				statusMsg += " Byte not successfully interpreted."
				raise Exception(statusMsg)
			success = False
			dataIndex += 1
			lineIndex += 1

		return dataIndex, lineNumber, lineIndex

	
	@staticmethod
	def rewindOneByte(dataIndex, lineNumber, lineIndex):
		dataIndex -= 1
		lineIndex -= 1
		# if the current byte is a newline byte, then lineIndex will now be -1.
		if lineIndex == -1:
			lineIndex = 0
			lineNumber -=1
		return dataIndex, lineNumber, lineIndex

	@property
	def className(self):
		return self.__class__.__name__

	def __str__(self):
		return "Entry: [{} bytes]".format(len(self.data))

	@property
	def nb(self): # nb = number of bytes
		return len(self.data)
	
	def treeLines(self):
		treeLine = " " + str(self)
		n = 5 # display this number of bytes from either end of the Entry.
		m = self.nb
		if m <= n*2:
			treeLine += ": [{}]".format(repr(self.data))
		else:
			treeLine += ": [{} ... {}]".format(repr(self.data[:n], repr(self.data[-n:])))
		return [treeLine]








def stop(msg=None):
	if msg: print "\n%s\n" % msg
	import sys; sys.exit()


if __name__ == "__main__":
	main()
