from .. import util
import logging
from argparse import Namespace


# Set up logger for this module. By default, it produces no output.
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
log = logger.info
deb = logger.debug


def setup(args=Namespace()):
	args.logger = logger
	# Configure logger for this module.
	util.moduleLogger.configureModuleLogger(args)




# More imports.
confirmNoArgs = util.misc.confirmNoArgs
getRequiredItems = util.misc.getRequiredItems
getOptionalItems = util.misc.getOptionalItems
DotDict = util.DotDictionary.DotDict




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
ESCAPED = 10
contextNames = {0: 'EMPTY', 1: 'START_TAG_OPEN', 2: 'START_TAG_NAME',
	3: 'START_TAG_CLOSE', 4: 'TAG_OPEN', 5: 'INSIDE_ELEMENT',
	6: 'END_TAG_OPEN', 7: 'END_TAG_NAME', 8: 'END_TAG_CLOSE',
	9: 'DATA', 10: 'ESCAPED'
}
# END IMMUTABLE DATA




# NOTES:
# - The various indices used for tracking position within the data (e.g. lineNumber) are only used during the processing of an entire Element from a string value, primarily for the detection of errors. As changes are made to the Element (e.g. changing Entry values, adding new Elements), these indices will become inaccurate. They should not be used after the initial construction of the Element.




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
	e3 = Element.fromString(data=text3, loggers=[logger])
	print e3.foo.bar




class Element(object):
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
		self.lineNumber = 1 # text editors start at line number 1.
		self.lineIndex = 0
		self.finalDataIndex = 0
		self.finalLineNumber = 0
		self.finalLineIndex = 0
	
	
	def hello(self):
		log('hello')
		return "world"


	@classmethod
	def fromFile(klass, filePath):
		with open(filePath) as f:
			text = f.read()
			text = text.rstrip('\n') # remove final newline if it exists.
		return Element.fromString(data=text)


	def writeToFile(self, filePath):
		with open(filePath, 'w') as f:
			f.write(self.data)
			f.write('\n')
	

	def writeToNewFile(self, filePath):
		if os.path.isfile(filePath):
			raise OSError("File exists.")
		self.writeToFile(filePath)


	@classmethod
	def fromString(self, *args, **kwargs):
		# both the root element and any child elements are built using this method.
		confirmNoArgs(args)
		required = 'data:s'
		data = getRequiredItems(kwargs, required)
		optional = 'parent, dataLength:i, dataIndex:i, lineNumber:i, lineIndex:i, recursiveDepth:i'
		defaults = (None, len(data), 0, 1, 0, 0)
		parent, dataLength, dataIndex, lineNumber, lineIndex, recursiveDepth = getOptionalItems(kwargs, optional, defaults)
		e = Element()
		# process data into an Element tree.
		parameters = DotDict(kwargs)
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
		# Together, fromString and processString are a recursive function. fromString will be called on the next Element that we find, and it will then call this function.
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
		confirmNoArgs(args)
		required = 'parent, data:s, dataLength:i, dataIndex:i, lineNumber:i, lineIndex:i, recursiveDepth:i'
		parent, data, dataLength, dataIndex, lineNumber, lineIndex, recursiveDepth = getRequiredItems(kwargs, required)
		self.parent = parent
		self.dataIndex = dataIndex
		self.lineNumber = lineNumber
		self.lineIndex = lineIndex
		self.recursiveDepth = recursiveDepth
		parameters = DotDict(kwargs)
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
				elif context in [START_TAG_CLOSE, INSIDE_ELEMENT]:
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
				if context in [START_TAG_CLOSE, INSIDE_ELEMENT]:
					deb("Switch to Entry.")
					parameters.dataIndex = dataIndex
					if byte == '\n': lineNumber -= 1 # we added 1 at the start of this loop.
					parameters.lineNumber = lineNumber
					parameters.lineIndex = lineIndex
					parameters.parent = self
					entry, dataIndex, lineNumber, lineIndex = Entry.fromString(**parameters)
					self.children.append(entry)
					context = INSIDE_ELEMENT
					success = True

					


			if not success:
				statusMsg = statusMsg.format(c=contextNames[context], b=repr(byte), di=dataIndex, ln=lineNumber, li=lineIndex)
				statusMsg += " Previous bytes: [{p}]. Byte not successfully interpreted.".format(p=data[dataIndex-50:dataIndex])
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
	def isEntry(self):
		return False


	@property
	def isElement(self):
		return True


	@property
	def elementChildren(self):
		for child in self:
			if child.isElement:
				yield child


	@property
	def elementChildrenNames(self):
		return [c.name for c in self.elementChildren]


	@property
	def entryChildren(self):
		for child in self:
			if child.isEntry:
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
	def isLeaf(self):
		if self.nc == 0:
			return True
		if self.nc == 1 and self.child[0].className == "Entry":
			return True
		return False


	@property
	def text(self):
		# Get only the text contained by the element. Ignore its element children.
		if self.nc == 0: return ''
		return ''.join([child.data for child in self.entryChildren])


	@property
	def value(self):
		# This is for accessing values stored in leaf elements that need to be used for something. Whitespace makes using them difficult.
		if not self.isLeaf:
			raise ValueError('{} is not a leaf element.'.format(self))
		return self.deleteWhitespace(self.text)


	@property
	def data(self):
		data = self.startTag
		for child in self.children:
			if child.isEntry:
				data += child.data
			elif child.isElement:
				data += child.data
		data += self.endTag
		return data


	@property
	def escapedData(self):
		# insert backslash before any escape characters.
		data = self.startTag
		for child in self.children:
			if child.isEntry:
				data += child.escapedData
			elif child.isElement:
				data += child.escapedData
		data += self.endTag
		return data


	@staticmethod
	def deleteWhitespace(s):
		return s.translate(None, whitespaceCharacters)


	@property
	def entryData(self):
		data = ''
		for child in self.entryChildren:
			data += child.data
		return data


	@property
	def branchValue(self):
		# This is for accessing values stored in branch elements (which can contain other elements) that need to be used for something. Whitespace makes using these values difficult.
		return self.deleteWhitespace(self.entryData)


	@staticmethod
	def isElementName(name):
		for char in name:
			if char not in elementNameCharacters:
				return False
		return True


# example tree:
# <article>
# <title>James_Sullivan_on_the_nature_of_banks</title>
# <author_name>stjohn_piano</author_name>
# <author_name>Demo second author name</author_name>
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
	# 3) content/list/@name (all name elements that are direct children of the content/list element)
	# 4) //@name (all name elements contained within the article element)
	# notes:
	# - the result is always a list, which may be empty. use other wrapper functions to return more specific results (e.g. get exactly one result or raise error).


	def get(self, xpath):
		if xpath == '': return [self]
		if len(xpath) >= 3:
			if xpath[:3] == '//@':
				name = xpath[3:]
				if not self.isValidElementName(name):
					raise ValueError("xpath {x} contains an invalid element name.".format(x=xpath))
				result = self.getElementDescendantsWithName(name)
				return result
		if '/' not in xpath:
			name = xpath
			multiple = False
			if name[0] == '@':
				multiple = True
				name = name[1:]
			result = self.getElementChildrenWithName(name)
			if multiple == False:
				if len(result) != 1:
					raise ValueError("xpath {x} specified 1 child, but {n} found.".format(x=repr(xpath), n=len(result)))
			return result
		else:
			sections = xpath.split('/')
			name = sections[0]
			restOfPath = '/'.join(sections[1:])
			multiple = False
			if name[0] == '@':
				multiple = True
				name = name[1:]
			result1 = self.getElementChildrenWithName(name)
			if multiple == False:
				if len(result1) > 1:
					raise ValueError("xpath {x} specified 1 child, but {n} found.".format(x=repr(xpath), n=len(result1)))
			result2 = []
			for child in result1:
				result3 = child.get(restOfPath)
				result2.extend(result3)
			return result2
		raise Exception("Shouldn't arrive at the end of this function.")


	def getOne(self, xpath):
		items = self.get(xpath)
		if len(items) != 1:
			raise ValueError("Expected 1 items, but got {n}.".format(n=len(items)))
		return items[0]


	def getValue(self, xpath):
		return self.getOne(xpath).value


	def getBranchValue(self, xpath):
		return self.getOne(xpath).branchValue


	def getAll(self, xpath):
		items = self.get(xpath)
		if len(items) == 0:
			raise ValueError("Expected at least 1 items, but got 0.")
		return items


	def getElementChildrenWithName(self, name):
		items = []
		for child in self.elementChildren:
			if child.name == name:
				items.append(child)
		return items


	def getElementDescendantsWithName(self, name):
		items = []
		items.extend(self.getElementChildrenWithName(name))
		for child in self.elementChildren:
			items.extend(child.getElementDescendantsWithName(name))
		return items


	def getOneByValue(self, xpath, value):
		items = self.getAll(xpath)
		items = [x for x in items if x.value == value]
		if len(items) != 1:
			raise KeyError
		return items[0]


	def getOneByEntryData(self, xpath, value):
		items = self.getAll(xpath)
		items = [x for x in items if x.entryData == value]
		if len(items) != 1:
			raise KeyError
		return items[0]


	def getIndex(self):
		# look through siblings, and find our own index among them.
		# nameIndex allows this method to choose one child from among several with the same name.
		if self.parent == None:
			raise AttributeError
		for i, child in enumerate(self.parent.children):
			if id(child) == id(self):
				return i
		raise KeyError


	def getIndexByValue(self, xpath, value):
		element = self.getOneByValue(xpath, value)
		return element.getIndex()


	def setValue(self, value):
		if not self.isLeaf:
			raise ValueError
		# Result: This leaf Element has a single Entry child with the new value.
		entry = Entry.fromValue(value)
		entry.parent = self
		self.children = [entry]
	
	
	def add(self, item, index=None):
		if index == None: index = self.nc
		if index < 0 or index > self.nc:
			raise ValueError
		if item.className not in ['Element', 'Entry']:
			raise TypeError
		self.children.insert(index, item)

	
	def addAll(self, items, index=None):
		if not isinstance(items, list): raise TypeError
		if index == None: index = self.nc
		for i, item in enumerate(items):
			self.add(item, index + i)


	@property
	def prevSibling(self):
		i = self.getIndex()
		parent = self.parent
		if i == 0: raise KeyError
		return parent.children[i-1]

	
	@property
	def nextSibling(self):
		i = self.getIndex()
		parent = self.parent
		if i == parent.nc - 1: raise KeyError
		return parent.children[i+1]

	
	def detach(self, element):
		# This removes an element from the list of its parent's children.
		# Note: This doesn't actually make use of self, so it's not really a method.
		# However, this is easier to handle mentally as a sibling of setValue, get, add, etc.
		i = element.getIndex()
		children = element.parent.children
		element.parent.children = children[:i] + children[i+1:]
	

	def detachAll(self, items):
		if not isinstance(items, list): raise TypeError
		for item in items:
			self.detach(item)
	

	def search(self, searchString):
		lineNumbers = []
		for child in self.children:
			if child.isEntry:
				for i in self.findall(searchString, child.data):
					newLines = child.data[:i].count('\n')
					itemLineNumber = child.lineNumber + newLines
					lineNumbers.append(itemLineNumber)
			elif child.isElement:
				lineNumbers.extend(child.search(searchString))
		return lineNumbers


	@staticmethod
	def findall(p, s):
		# Yields all the positions of the pattern p in the string s.
		i = s.find(p)
		while i != -1:
			yield i
			i = s.find(p, i+1)




















class Entry:


	def __init__(self):
		self.data = "" # this contains the actual data in bytes of the Entry (after escape characters have been removed)
		self.parent = None
		# dataIndex, lineNumber, and lineIndex exist with reference to the original data (which includes escape characters). They record the location of the start of an entry.
		self.dataIndex = 0
		self.lineNumber = 0
		self.lineIndex = 0
		
	
	@classmethod
	def fromValue(self, value):
		# This is for creating a new Entry that will be inserted into an existing Element.
		for byte in value:
			if byte not in entryCharacters:
				raise ValueError
		entry = Entry()
		entry.data = value
		return entry

	
	@classmethod
	def fromString(self, *args, **kwargs):
		confirmNoArgs(args)
		entry = Entry()
		# process data into an Entry.
		dataIndex, lineNumber, lineIndex = entry.processString(**kwargs)
		nBytes = len(entry.data)
		z = 10 # how much of the entry's start/end data to show in the log.
		value = entry.data
		if nBytes > 2 * z:
			value = value[:z] + "..." + value[-z:]
		value = repr(value)
		deb("Entry parsed. Length = {n} bytes. Value = {v}.".format(n=nBytes, v=value))
		return entry, dataIndex, lineNumber, lineIndex


	def processString(self, *args, **kwargs):
		# Notes:
		# - An entry consists of at least one printable ASCII byte.
		confirmNoArgs(args)
		required = 'data:s, dataLength:i, dataIndex:i, lineNumber:i, lineIndex:i, parent'
		data, dataLength, dataIndex, lineNumber, lineIndex, parent = getRequiredItems(kwargs, required)
		self.dataIndex = dataIndex
		self.lineNumber = lineNumber
		self.lineIndex = lineIndex
		self.parent = parent
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
				elif context == ESCAPED:
					self.data += byte
					context = DATA
					success = True

			elif byte == ">":
				pass

			elif byte == "\\":
				if context == DATA:
					# The next character will treated as "escaped".
					context = ESCAPED
					success = True
				elif context == ESCAPED:
					self.data += byte
					context = DATA
					success = True

			elif byte in entryCharacters:
				if context == DATA:
					self.data += byte
					success = True


			if not success:
				statusMsg = statusMsg.format(c=contextNames[context], b=repr(byte), di=dataIndex, ln=lineNumber, li=lineIndex)
				statusMsg += " Previous bytes: [{p}]. Byte not successfully interpreted.".format(p=data[dataIndex-50:dataIndex])
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
			treeLine += ": [{} ... {}]".format(repr(self.data[:n]), repr(self.data[-n:]))
		return [treeLine]


	@property
	def isEntry(self):
		return True


	@property
	def isElement(self):
		return False


	def getIndex(self):
		# look through siblings, and find our own index among them.
		# nameIndex allows this method to choose one child from among several with the same name.
		if self.parent == None:
			raise Exception
		for i, child in enumerate(self.parent.children):
			if id(child) == id(self):
				return i
		raise KeyError


	@property
	def prevSibling(self):
		i = self.getIndex()
		parent = self.parent
		if i == 0: raise KeyError
		return parent.children[i-1]

	
	@property
	def nextSibling(self):
		i = self.getIndex()
		parent = self.parent
		if i == parent.nc - 1: raise KeyError
		return parent.children[i+1]


	@property
	def escapedData(self):
		# insert backslash before any escape characters.
		result = ''
		for c in self.data:
			if c in escapedCharacters:
				result += "\\" + c
			else:
				result += c
		return result










def stop(msg=None):
	if msg: print "\n%s\n" % msg
	import sys; sys.exit()


if __name__ == "__main__":
	main()
