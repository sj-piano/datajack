# Imports
import logging
import string
import json




# Relative imports
from .. import util




# Shortcuts
v = util.validate




# Set up logger for this module. By default, it produces no output.
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
logger.setLevel(logging.ERROR)
log = logger.info
deb = logger.debug




def setup(
    log_level = 'error',
    debug = False,
    log_timestamp = False,
    log_file = None,
    ):
  # Configure logger for this module.
  util.module_logger.configure_module_logger(
    logger = logger,
    logger_name = __name__,
    log_level = log_level,
    debug = debug,
    log_timestamp = log_timestamp,
    log_file = log_file,
  )
  deb('Setup complete.')




# IMMUTABLE DATA
element_name_characters = "0123456789abcdefghijklmnopqrstuvwxyz_-."
entry_characters = "!#$%&'()*+,-./0123456789:;=?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[]^_`abcdefghijklmnopqrstuvwxyz{|}~"
entry_characters += "\""
escaped_characters = "<>\\"
whitespace_characters = " \t\n"
entry_characters += escaped_characters + whitespace_characters
# Define contexts.
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
context_names = {
  0: 'EMPTY', 1: 'START_TAG_OPEN', 2: 'START_TAG_NAME',
  3: 'START_TAG_CLOSE', 4: 'TAG_OPEN', 5: 'INSIDE_ELEMENT',
  6: 'END_TAG_OPEN', 7: 'END_TAG_NAME', 8: 'END_TAG_CLOSE',
  9: 'DATA', 10: 'ESCAPED'
}
# END IMMUTABLE DATA




# NOTES:
# - The various indices used for tracking position within the data (e.g. line_number) are only used during the processing of an entire Element from a string value, primarily for the detection of errors. As changes are made to the Element (e.g. changing Entry values, adding new Elements), these indices will become inaccurate. They should not be used after the initial construction of the Element.




class Element(object):
  """EML object"""


  def __init__(self):
    self.name = ""
    self.end_name = ""
    self.complete = False
    self.children = []
    self.parent = None
    self.logger = None
    # data_index, line_number, and line_index exist with reference to the original data (which includes escape characters). They record the location of the start of an element.
    self.data_index = 0
    self.line_number = 1  # Text editors start at line number 1.
    self.line_index = 0
    self.final_data_index = 0
    self.final_line_number = 0
    self.final_line_index = 0
    self.recursive_depth = 0
    self.verbose = False


  def hello(self):
    log('hello')
    return 'world'


  @classmethod
  def from_file(cls, file):
    with open(file) as f:
      text = f.read()
      text = text.rstrip('\n')  # Remove final newline if it exists.
    return Element.from_string(data=text)


  def write_to_file(self, file):
    with open(file, 'w') as f:
      f.write(self.data)
      f.write('\n')


  def write_to_new_file(self, file):
    if os.path.isfile(file):
      raise OSError('File exists.')
    self.writeToFile(file)


  @classmethod
  def from_string(
      cls,
      # data and data_length are not stored as element attributes.
      data=None,
      data_length=None,
      parent=None,
      data_index=0,
      line_number=1,
      line_index=0,
      recursive_depth=0,
      verbose=False,
      ):
    # Note: The root element and any child elements are built using this method.
    if data is None:
      raise ValueError
    if data_length is None:
      data_length = len(data)  # default value.
    # Validate input.
    location = 'datajack/code/Element.py:Element:from_string()'
    v.validate_string(data, 'data', location)
    v.validate_positive_integer(data_length, 'data_length', location)
    v.validate_whole_number(data_index, 'data_index', location)
    v.pi(line_number, 'line_number', location)
    v.wn(line_index, 'line_index', location)
    v.wn(recursive_depth, 'recursive_depth', location)
    v.validate_boolean(verbose, 'verbose', location)
    # Process data into an Element tree.
    e = Element()
    e.parent = parent
    e.data_index = data_index
    e.line_number = line_number
    e.line_index = line_index
    e.recursive_depth = recursive_depth
    e.verbose = verbose
    if parent is None:
      deb("Begin parsing data into an Element tree.")
    e.process_string(data, data_length)
    if e.parent is None:
      deb("Element parsed. Name = '{name}'. Number of children = {c}.".format(name=e.name, c=e.nc))
    return e


  def process_string(self, data, data_length):
    # Together, from_string and process_string are a recursive function. from_string will be called on the next Element that we find, and it will then call this function.
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
    # -- EMPTY (we haven't started yet)
    # -- START_TAG_OPEN (we've processed the first character, which must be '<')
    # -- START_TAG_NAME (we're within the tagName of a start_tag)
    # -- START_TAG_CLOSE (we've just closed a start_tag)
    # -- TAG_OPEN (we've just opened a tag, but we don't yet know if it's this Element's end_tag or a child Element's start_tag)
    # -- INSIDE_ELEMENT (we're inside an unfinished Element, and we've just finished a child Element or Entry)
    # -- END_TAG_OPEN, END_TAG_NAME, END_TAG_CLOSE
    # - Approach: As we encounter each character, we interpret it based on the current context.
    # Load stored values from self.
    parent = self.parent
    data_index = self.data_index
    line_number = self.line_number
    line_index = self.line_index
    recursive_depth = self.recursive_depth
    verbose = self.verbose
    if parent is not None:
      if verbose:
        deb("Switch to new Element")
    # Status message template
    status_msg = "Element: context [{c}], byte [{b}], data_index [{di}], line_number [{ln}], line_index [{li}], recursive_depth [{r}]."
    # Set initial context.
    context = EMPTY
    # We test for (byte + context) combination that we're interested in, and raise an Error if we get any other combination.
    success = False  # Have we successfully interpreted the current byte?
    while True:

      try:
        byte = data[data_index]
      except IndexError as e:
        status_msg = status_msg.format(
          c=context_names[context], b=repr(byte), di=data_index,
          ln=line_number, li=line_index, r=recursive_depth
        )
        status_msg += " No more data left, but Element is not complete."
        raise Exception(status_msg)

      if byte == "\n":  # We've moved to a new line.
        line_index = 0
        line_number += 1

      if verbose:
        deb(status_msg.format(
          c=context_names[context], b=repr(byte), di=data_index,
          ln=line_number, li=line_index, r=recursive_depth
        ))

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
          deb("New Element: name = '{}'".format(self.name))
          context = START_TAG_CLOSE
          success = True
        elif context == END_TAG_NAME:
          context = END_TAG_CLOSE
          # We've arrived at the end of this Element.
          if self.name != self.end_name:
            status_msg = status_msg.format(
              c=context_names[context], b=repr(byte), di=data_index,
              ln=line_number, li=line_index, r=recursive_depth
            )
            status_msg += " Finished building Element, but end_tagName ({e}) is not the same as start_tagName ({s}).".format(e=self.end_name, s=self.name)
            raise Exception(status_msg)
          self.final_data_index = data_index
          self.final_line_number = line_number
          self.final_line_index = line_index
          self.complete = True
          if parent is not None:
            deb("Element parsed. Name = '{name}'. Number of children = {c}.".format(name=self.name, c=len(self.children)))
          break

      elif byte == "/":
        if context == TAG_OPEN:
          context = END_TAG_OPEN
          success = True
        elif context == START_TAG_CLOSE:
          deb("Switch to new Entry.")
          entry, data_index, line_number, line_index = Entry.from_string_section(
            data=data, data_length=data_length,
            parent=self, data_index=data_index,
            line_number=line_number, line_index=line_index,
            recursive_depth=recursive_depth+1, verbose=verbose,
          )
          self.children.append(entry)
          context = INSIDE_ELEMENT
          success = True

      elif byte in element_name_characters:
        if context == START_TAG_OPEN:
          context = START_TAG_NAME
          self.name += byte
          success = True
        elif context == START_TAG_NAME:
          self.name += byte
          success = True
        elif context in [START_TAG_CLOSE, INSIDE_ELEMENT]:
          deb("Switch to new Entry.")
          entry, data_index, line_number, line_index = Entry.from_string_section(
            data=data, data_length=data_length,
            parent=self, data_index=data_index,
            line_number=line_number, line_index=line_index,
            recursive_depth=recursive_depth+1, verbose=verbose,
          )
          self.children.append(entry)
          context = INSIDE_ELEMENT
          success = True
        elif context == END_TAG_OPEN:
          context = END_TAG_NAME
          self.end_name += byte
          success = True
        elif context == END_TAG_NAME:
          self.end_name += byte
          success = True
        elif context == TAG_OPEN:
          deb("Switch to child Element.")
          data_index, line_number, line_index = self.rewind_bytes(1, data_index, line_number, line_index)
          child = Element.from_string(
            data=data, data_length=data_length,
            parent=self, data_index=data_index,
            line_number=line_number, line_index=line_index,
            recursive_depth=recursive_depth+1, verbose=verbose,
          )
          self.children.append(child)
          data_index = child.final_data_index
          line_number = child.final_line_number
          line_index = child.final_line_index
          context = INSIDE_ELEMENT
          success = True

      elif byte in entry_characters:
        if context in [START_TAG_CLOSE, INSIDE_ELEMENT]:
          deb("Switch to Entry.")
          if byte == '\n':
            # We added 1 at the start of this loop.
            line_number -= 1
          entry, data_index, line_number, line_index = Entry.from_string_section(
            data=data, data_length=data_length,
            parent=self, data_index=data_index,
            line_number=line_number, line_index=line_index,
            recursive_depth=recursive_depth+1, verbose=verbose,
          )
          self.children.append(entry)
          context = INSIDE_ELEMENT
          success = True




      if not success:
        status_msg = status_msg.format(
          c=context_names[context], b=repr(byte), di=data_index,
          ln=line_number, li=line_index, r=recursive_depth
        )
        status_msg += " Previous bytes: [{p}]. Byte not successfully interpreted.".format(p=data[data_index-50:data_index])
        # During normal processing, we try to only enumerate goodness (i.e. whitelist).
        # Here, we enumerate badness, and try to produce a helpful error message if possible.
        error_msg = ''
        if context == START_TAG_NAME:
          if byte not in element_name_characters:
            error_msg = 'Tag names can only contain characters in the element_name_characters list: [{}]'.format(element_name_characters)
        if error_msg:
          error_msg = '\n\nERROR: ' + error_msg + '\n'
        raise Exception(status_msg + error_msg)


      success = False
      data_index += 1
      line_index += 1


    if self.parent is None:
      # This is the root Element of the data.
      # If there is any data left over, this is an error.
      if data_index < data_length - 1:
        remaining_data = data[data_index+1:]
        _msg = "Finished building root element, but there is remaining data: {}".format(repr(remaining_data))
        raise ValueError(_msg)


    return self




  def rewind_bytes(self, n_bytes, data_index, line_number, line_index):
    # This doesn't handle newline bytes.
    for i in range(n_bytes):
      data_index -= 1
      line_index -= 1
    return data_index, line_number, line_index


  def __str__(self):
    return "Element: [{}]".format(self.name)


  def __iter__(self):
    for child in self.children:
      yield child


  @property
  def is_entry(self):
    return False


  @property
  def is_element(self):
    return True


  @property
  def child(self):
    return self.children


  @property
  def element_children(self):
    return [c for c in self.children if c.is_element]


  @property
  def element_child(self):
    # Use: e5.element_child[0].name
    return self.element_children


  @property
  def element_children_names(self):
    return [c.name for c in self.element_children]


  @property
  def entry_children(self):
    return [c for c in self.children if c.is_entry]


  @property
  def element_descendants(self):
    items = []
    items.extend(self.element_children)
    for child in self.element_children:
      items.extend(child.element_descendants)
    return items


  @property
  def start_tag(self):
    return "<" + self.name + ">"


  @property
  def end_tag(self):
    return "</" + self.end_name + ">"


  @property
  def nc(self):
    # Calculate number of children.
    return len(self.children)


  @property
  def class_name(self):
    return self.__class__.__name__


  @property
  def tree(self):
    return "\n".join(self.tree_lines())


  @property
  def element_tree(self):
    return "\n".join(self.tree_lines(elements_only=True)).strip()


  def tree_lines(self, elements_only=False):
    if self.parent is None:
      tree_lines = ["Tree for " + str(self)]
    elif elements_only:
      tree_lines = [" " + self.name]
    else:
      tree_lines = [" " + str(self)]
    for child in self:
      if elements_only and child.is_entry:
        continue
      child_lines = child.tree_lines(elements_only)
      child_lines = [("-" + x) for x in child_lines]
      tree_lines.extend(child_lines)
    return tree_lines


  @property
  def is_leaf(self):
    if self.nc == 0:
      return True
    if self.nc == 1 and self.child[0].class_name == "Entry":
      return True
    return False


  @property
  def text(self):
    # Get only the text contained by the element. Ignore its element children.
    if self.nc == 0:
      return ''
    return ''.join([child.data for child in self.entry_children])


  @property
  def value(self):
    # This is for accessing values stored in leaf elements that need to be used for something. Whitespace makes using them difficult.
    if not self.is_leaf:
      raise ValueError('{} is not a leaf element.'.format(self))
    return self.delete_whitespace(self.text)


  @property
  def data(self):
    data = self.start_tag
    for child in self.children:
      if child.is_entry:
        data += child.escaped_data
      elif child.is_element:
        data += child.data
    data += self.end_tag
    return data


  @property
  def content(self):
    # Same as .data, except without the topmost element's start and end tags.
    # The tags of the children are included.
    n1 = len(self.start_tag)
    n2 = len(self.end_tag)
    result = self.data[n1:-n2]
    return result


  @property
  def escaped_data(self):
    # Insert backslash before any escaped characters.
    data = self.start_tag
    for child in self.children:
      if child.is_entry:
        data += child.escaped_data
      elif child.is_element:
        data += child.escaped_data
    data += self.end_tag
    return data


  @staticmethod
  def delete_whitespace(s):
    new_chars = ' ' * len(whitespace_characters)
    table = str.maketrans(whitespace_characters, new_chars)
    return s.translate(table)


  @property
  def entry_data(self):
    data = ''
    for child in self.entry_children:
      data += child.data
    return data


  @property
  def branch_value(self):
    # This is for accessing values stored in branch elements (which can contain other elements) that need to be used for something. Whitespace makes using these values difficult.
    return self.delete_whitespace(self.entry_data)


  @staticmethod
  def is_element_name(name):
    for char in name:
      if char not in element_name_characters:
        return False
    return True


# Example tree:
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

  # possible xs:
  # - title (the title element that is a direct child of the root 'article' element)
  # - author_name (all author_name elements that are direct children of the root 'article' element)
  # - content/list/title (the title element that is a particular descendant of the root article element)
  # - content/list/name (all name elements that are direct children of the content/list element)
  # - //name (all name elements contained within the article element)
  # - link[@type='asset'] (single link child that has a 'type' child with value='asset')
  # - content/link[@type='asset'] (all content/link elements that have a 'type' child with value='asset')
  # - //list[@title='Guild_Members'][@name='StJohn_Piano']
  # notes:
  # - the result is always a list, which may be empty. use other wrapper functions to return more specific results (e.g. get exactly one result or raise error).


  def get(self, x):
    # Working principle: Handle any prefixes. Then handle the first section of the xpath. Then recurse.
    deb('xpath: ' + x)
    xOriginal = x
    # xpath: ''
    if x == '':
      return [self]
    # Handle double-slash at begining.
    # xpath: //name
    descendants = False
    if len(x) > 2:
      if x[:2] == '//':
        x = x[2:]
        descendants = True
        #if self.is_element_name(name):
        #  return self.get_element_descendants_with_name(name)
    # xpaths that contain sections split by '/'
    # x: 'content/list/title'
    x2 = None
    if x.count('/') > 0:
      sections = x.split('/')
      x = sections[0]  # We process only the first section of path.
      x2 = '/'.join(sections[1:])  # Rest of path.
    # Get predicate if it exists.
    # xpath: link[type='asset']
    # xpath: //list[@title='Guild_Members'][@name='StJohn_Piano']
    # xpath: structure/number_of_columns/row[1]/index
    predicates = {}
    number = None
    if x.count('[') > 0:
      sections = x.split('[')
      x = sections[0]
      ps = sections[1:]
      for p in ps:
        p = p.replace('@', '').replace(']', '')
        if '=' in p:
          k, v = p.split('=')
          v = v.replace("'", "")
          predicates[k] = v
        elif p.isdigit():  # e.g. [1]
          number = int(p)
        else:
          raise Exception
    # Get children / descendants that match conditions.
    elements = []
    if not self.is_element_name(x):
      raise ValueError(x)
    if descendants:
      elements = self.get_element_descendants_with_name(x)
    else:
      elements = self.get_element_children_with_name(x)
    if number is not None:  # e.g. [1] predicate.
      elements = [elements[number]]
    for k, v in iter(predicates.items()):
      elements = [e for e in elements if e.get_value_if_exists(k) == v]
    if x2:
      elements2 = []
      for e in elements:
        elements2.extend(e.get(x2))
      elements = elements2
    return elements


  def get_one(self, xpath):
    items = self.get(xpath)
    if len(items) != 1:
      raise ValueError("Expected 1 item, but got {n}.".format(n=len(items)))
    return items[0]


  def get_value(self, xpath):
    return self.get_one(xpath).value


  def get_if_exists(self, xpath):
    r = self.get(xpath)
    if len(r) == 0:
      return None
    elif len(r) > 1:
      msg = "Expected exactly 0 or 1 result for xpath={}. Instead, found {} results."
      msg = msg.format(repr(xpath), len(r))
      raise ValueError(msg)
    return r[0]


  def get_value_if_exists(self, xpath):
    r = self.get_if_exists(xpath)
    if r is None:
      return None
    return r.value


  def get_branch_value(self, xpath):
    return self.get_one(xpath).branch_value


  def get_all(self, xpath):
    items = self.get(xpath)
    if len(items) == 0:
      raise ValueError("Expected at least 1 item, but got 0.")
    return items


  def get_values(self, xpath):
    return [x.value for x in self.get_all(xpath)]


  def get_element_children_with_name(self, name):
    items = []
    for child in self.element_children:
      if child.name == name:
        items.append(child)
    return items


  def get_element_descendants_with_name(self, name):
    items = []
    items.extend(self.get_element_children_with_name(name))
    for child in self.element_children:
      items.extend(child.get_element_descendants_with_name(name))
    return items


  def get_one_by_value(self, xpath, value):
    items = self.get_all(xpath)
    items = [x for x in items if x.value == value]
    if len(items) != 1:
      raise KeyError
    return items[0]


  def get_one_by_entry_data(self, xpath, value):
    items = self.get_all(xpath)
    items = [x for x in items if x.entry_data == value]
    if len(items) != 1:
      raise KeyError
    return items[0]


  def get_index(self):
    # Look through siblings, and find our own index among them.
    if self.parent is None:
      raise AttributeError
    for i, child in enumerate(self.parent.children):
      if id(child) == id(self):
        return i
    raise KeyError


  def get_index_by_value(self, xpath, value):
    element = self.get_one_by_value(xpath, value)
    return element.get_index()


  def set_value(self, value):
    if not self.is_leaf:
      raise ValueError
    # Result: This leaf Element has a single Entry child with the new value.
    entry = Entry.from_string(value)
    entry.parent = self
    self.children = [entry]


  def add(self, item, index=None):
    if index is None:
      index = self.nc
    if index < 0 or index > self.nc:
      raise ValueError
    if item.class_name not in ['Element', 'Entry']:
      raise TypeError
    self.children.insert(index, item)


  def add_all(self, items, index=None):
    if not isinstance(items, list):
      raise TypeError
    if index is None:
      index = self.nc
    for i, item in enumerate(items):
      self.add(item, index + i)


  @property
  def path_from_root(self):
    # This path should be usable as the xpath argument to the get() method.
    if self.recursive_depth == 0:
      return ''
    if self.recursive_depth == 1:
      return self.name
    p = self.parent
    path = p.name + '/' + self.name
    while p.recursive_depth > 1:
      p = p.parent
      path = p.name + '/' + path
    return path


  @property
  def prev_sibling(self):
    i = self.get_index()
    parent = self.parent
    if i == 0:
      raise KeyError
    return parent.children[i-1]


  @property
  def next_sibling(self):
    i = self.get_index()
    parent = self.parent
    if i == parent.nc - 1:
      raise KeyError
    return parent.children[i+1]


  def has_child(self, name):
    n = self.element_children_names.count(name)
    if n > 1:
      raise ValueError
    if n == 1:
      return True
    return False


  def insert_child(self, input, index=None):
    # Notes:
    # - Insert the input element at the specified index in the list of children.
    # - If no index is specified, append the input element to the list of children.
    # - If index==len(self.children), append the input element to the list of children.
    # - If the input element is a string, make it into an Entry.
    # - Return the index at which the new element has been added to the list of children.
    n = self.nc
    if isinstance(input, Element) or isinstance(input, Entry):
      pass
    elif isinstance(input, str):
      input = Entry.from_string(input)
    else:
      raise ValueError
    if index is None:
      # Note: index could be 0, so don't use: 'if not index'
      index = n
    v.validate_integer(index)
    if index > n:
      raise ValueError
    if index > -1:
      if index in [n, -1]:
        self.children.append(input)
      else:
        self.children.insert(index, input)
      return index
    # Handle negative indices.
    # We shift once to the right.
    # This means that using index=-2 will insert the input at the second-to-last position.
    # Use index -(n + 1) to insert the input at the first position.
    if index < (-n):
      raise ValueError
    index_original = index
    index += 1
    self.children.insert(index, input)
    return index_original


  def pop_child(self, name):
    child = self.get_one(name)
    self.detach(child)
    return child


  def detach(self, element):
    # This removes an element from the list of its parent's children.
    # Note: This doesn't actually make use of self, so it's not really a method.
    # However, this is easier to handle mentally as a sibling of set_value, get, add, etc.
    i = element.get_index()
    children = element.parent.children
    element.parent.children = children[:i] + children[i+1:]


  def detach_all(self, items):
    if not isinstance(items, list):
      raise TypeError
    for item in items:
      self.detach(item)


  def replace(self, name, new_child_element):
    # Replace a child with another element.
    # Note: "name" can be a path.
    child = self.get_one(name)
    i = child.get_index()
    child.parent.children[i] = new_child_element


  def search(self, search_string):
    line_numbers = []
    for child in self.children:
      if child.is_entry:
        for i in self.findall(search_string, child.data):
          new_lines = child.data[:i].count('\n')
          item_line_number = child.line_number + new_lines
          line_numbers.append(item_line_number)
      elif child.is_element:
        line_numbers.extend(child.search(search_string))
    return line_numbers


  @staticmethod
  def find_all(p, s):
    # Yields all the positions of the pattern p in the string s.
    i = s.find(p)
    while i != -1:
      yield i
      i = s.find(p, i+1)


  def contains_tree_of(self, other, recursive_depth = 1):
    # other = other element
    msg = ""
    result = False
    for child in other.element_children:
      if child.name not in self.element_children_names:
        msg += "\nMessage from Element parsing:"
        msg += " Expected to find child element {} at level {}" \
          .format(repr(child.name), recursive_depth)
        msg += ", but did not."
        return result, msg
      # Select children with this particular element name.
      # Then recursively check that each of these contains the tree of the other's child.
      selected = self.get_element_children_with_name(child.name)
      for child2 in selected:
        result2, msg2 = child2.contains_tree_of(child, recursive_depth+1)
        if not result2:
          return result2, msg2
    result = True
    return result, msg


  def matches_tree_of(self, other):
    # other = other element
    msg = ""
    result = False
    x = sorted(self.element_children_names)
    y = sorted(other.element_children_names)
    if x != y:
      msg += "\nMessage from Element parsing:"
      msg += "\nExpected that list of element children's names:"
      msg += "\n({})".format(str(x))
      msg += "\nwould match list of comparison element's list of element children's names:"
      msg += "\n({})".format(str(y))
      return result, msg
    # Recursively check each of the element children.
    # Compare each child against all the comparison element's children that have the same name.
    for child in self.element_children:
      selected = other.get_element_children_with_name(child.name)
      for child2 in selected:
        result2, msg2 = child.matches_tree_of(child2)
        if not result2:
          return result2, msg2
    result = True
    return result, msg


  def create_copy(self):
    return Element.from_string(self.escaped_data)


  @property
  def element_children_names_are_unique(self):
    names = self.element_children_names
    if len(names) == len(set(names)):
      return True
    return False


  def to_dict(self):
    if self.is_leaf:
      return {self.name: self.value}
    result = {self.name: {}}
    result_value = result[self.name]
    # We preserve Entry data only if the parent Element is a leaf element.
    for child in self.element_children:
      name = child.name
      if self.element_children_names.count(name) == 1:
        result_value.update(child.to_dict())
      # We translate multiple children with the same name into a list value.
      else:
        if name not in result_value.keys():
          result_value[name] = []
        if child.is_leaf:
          result_value[name].append(child.value)
        else:
          d = child.to_dict()
          value = list(d.values())[0]
          result_value[name].append(value)
    return result


  def to_json(self):
    d = self.to_dict()
    return json.dumps(d, sort_keys=True)


  def to_json_pretty(self):
    d = self.to_dict()
    return json.dumps(d, indent=2, sort_keys=True)


  @classmethod
  def from_dict(self, d=None, recursive_depth=0):
    if d is None:
      raise ValueError
    e = Element()
    keys = list(d.keys())
    if len(keys) != 1:
      raise KeyError
    e.name = keys[0]
    e.end_name = e.name
    e.recursive_depth = recursive_depth
    child_value = d[e.name]

    def n():
      # Add newlines to make the output more readable.
      return Entry.from_string('\n')

    if type(child_value) == str:
      child = Entry.from_string(child_value)
      e.children.append(child)
    elif type(child_value) == dict:
      for key, value in sorted(child_value.items()):
        # Make sure that value is a list, so that we can iterate over it.
        # This way, we translate a list to a sequence of Elements with the same name.
        if type(value) == list:
          values = value
        else:
          values = [value]
        for v in values:
          d2 = {key: v}
          child = Element.from_dict(d2, e.recursive_depth + 1)
          child.parent = self
          e.children.extend([n(), child])
      e.children.append(n())
    else:
      raise TypeError
    e.complete = True
    return e


  @classmethod
  def from_json(self, s=None):
    if s is None:
      raise ValueError
    d = json.loads(s)
    e = Element.from_dict(d)
    return e




















class Entry:


  def __init__(self):
    # self.data contains the actual data in bytes of the Entry (after the escape characters have been removed).
    self.data = ""
    self.parent = None
    # data_index, line_number, and line_index exist with reference to the original data (which includes escape characters). They record the location of the start of an entry.
    self.data_index = 0
    self.line_number = 0
    self.line_index = 0


  @classmethod
  def from_string(cls, value):
    # This is for creating a new standalone Entry (which will be inserted into an Element).
    if not isinstance(value, str):
      raise ValueError
    for byte in value:
      if byte not in entry_characters:
        raise ValueError
    entry = Entry()
    entry.data = value
    return entry


  # This is for creating an Entry object from a string section of data that we're processing into an Element.
  @classmethod
  def from_string_section(
      cls,
      # data and data_length are not stored as entry attributes.
      data=None,
      data_length=None,
      parent=None,
      data_index=0,
      line_number=1,
      line_index=0,
      recursive_depth=0,
      verbose=False,
      ):
    if data is None:
      raise ValueError
    if data_length is None:
      data_length = len(data)  # default value.
    # Validate input.
    location = 'datajack/code/Element.py:Entry:from_string()'
    v.validate_string(data, 'data', location)
    v.validate_positive_integer(data_length, 'data_length', location)
    v.validate_whole_number(data_index, 'data_index', location)
    v.pi(line_number, 'line_number', location)
    v.wn(line_index, 'line_index', location)
    v.wn(recursive_depth, 'recursive_depth', location)
    v.validate_boolean(verbose, 'verbose', location)
    # Process data into an Entry.
    entry = Entry()
    entry.parent = parent
    entry.data_index = data_index
    entry.line_number = line_number
    entry.line_index = line_index
    entry.recursive_depth = recursive_depth
    entry.verbose = verbose
    data_index, line_number, line_index = entry.process_string(
      data, data_length
    )
    n_bytes = len(entry.data)
    z = 10  # How much of the entry's start/end data to show in the log.
    value = entry.data
    if n_bytes > 2 * z:
      value = value[:z] + "..." + value[-z:]
    value = repr(value)
    deb("Entry parsed. Length = {n} bytes. Value = {v}.".format(n=n_bytes, v=value))
    return entry, data_index, line_number, line_index


  def process_string(self, data, data_length):
    # Notes:
    # - An entry consists of at least one printable ASCII byte.
    # Load stored values from self.
    data_index = self.data_index
    line_number = self.line_number
    line_index = self.line_index
    recursive_depth = self.recursive_depth
    verbose = self.verbose
    status_msg = "Entry: context [{c}], byte [{b}], data_index [{di}], line_number [{ln}], line_index [{li}], recursive_depth [{r}]."
    context = DATA
    # We test for (byte + context) combination that we're interested in, and raise an Error if we get any other combination.
    success = False  # Have we successfully interpreted the current byte?
    while True:

      try:
        byte = data[data_index]
      except IndexError as e:
        status_msg = status_msg.format(
          c=context_names[context], b=repr(byte), di=data_index,
          ln=line_number, li=line_index, r=recursive_depth
        )
        status_msg += " No more data left, but Element is not complete."
        raise Exception(status_msg)

      if byte == "\n":
        # We've moved to a new line.
        line_index = 0
        line_number += 1

      if verbose:
        deb(status_msg.format(
          c=context_names[context], b=repr(byte), di=data_index,
          ln=line_number, li=line_index, r=recursive_depth
        ))

      if byte == "<":
        if context == DATA:
          # We've encountered a new Element.
          # Rewind one byte so that the Element processing loop completes and begins again on this current byte.
          data_index, line_number, line_index = self.rewind_one_byte(
            data_index, line_number, line_index
          )
          break
        elif context == ESCAPED:
          self.data += byte
          context = DATA
          success = True

      elif byte == ">":
        if context == DATA:
          status_msg = status_msg.format(
            c=context_names[context], b=repr(byte), di=data_index,
            ln=line_number, li=line_index, r=recursive_depth
          )
          status_msg += " Encountered unescaped right angle bracket (>) in Entry data."
          raise Exception(status_msg)
        elif context == ESCAPED:
          self.data += byte
          context = DATA
          success = True

      elif byte == "\\":
        if context == DATA:
          # The next character will treated as "escaped".
          context = ESCAPED
          success = True
        elif context == ESCAPED:
          self.data += byte
          context = DATA
          success = True

      elif byte in entry_characters:
        if context == DATA:
          self.data += byte
          success = True


      if not success:
        status_msg = status_msg.format(
          c=context_names[context], b=repr(byte), di=data_index,
          ln=line_number, li=line_index, r=recursive_depth
        )
        status_msg += " Previous bytes: [{p}]. Byte not successfully interpreted.".format(p=data[data_index-50:data_index])
        raise Exception(status_msg)
      success = False
      data_index += 1
      line_index += 1

    return data_index, line_number, line_index


  @staticmethod
  def rewind_one_byte(data_index, line_number, line_index):
    data_index -= 1
    line_index -= 1
    # If the current byte is a newline byte, then line_index will now be -1.
    if line_index == -1:
      line_index = 0
      line_number -= 1
    return data_index, line_number, line_index


  @property
  def class_name(self):
    return self.__class__.__name__


  def __str__(self):
    return "Entry: [{} bytes]".format(len(self.data))


  @property
  def nb(self):  # nb = number of bytes
    return len(self.data)


  def tree_lines(self, elements_only=False):
    # elements_only arg included for compability with Element.tree_lines method
    tree_line = " " + str(self)
    n = 5  # Display this number of bytes from either end of the Entry.
    m = self.nb
    if m <= n*2:
      tree_line += ": [{}]".format(repr(self.data))
    else:
      tree_line += ": [{} ... {}]".format(repr(self.data[:n]), repr(self.data[-n:]))
    return [tree_line]


  @property
  def is_entry(self):
    return True


  @property
  def is_element(self):
    return False


  def get_index(self):
    # Look through siblings, and find our own index among them.
    if self.parent is None:
      raise Exception
    for i, child in enumerate(self.parent.children):
      if id(child) == id(self):
        return i
    raise KeyError


  @property
  def prev_sibling(self):
    i = self.get_index()
    parent = self.parent
    if i == 0:
      raise KeyError
    return parent.children[i-1]


  @property
  def next_sibling(self):
    i = self.get_index()
    parent = self.parent
    if i == parent.nc - 1:
      raise KeyError
    return parent.children[i+1]


  @property
  def escaped_data(self):
    # Insert backslash before any escaped characters.
    result = ''
    for c in self.data:
      if c in escaped_characters:
        result += "\\" + c
      else:
        result += c
    return result


  def create_copy(self):
    return Entry.from_string(self.escaped_data)









def stop(msg=None):
  if msg:
    print("\n%s\n" % msg)
  import sys
  sys.exit()

