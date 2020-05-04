#!/usr/bin/python


from Element import Element


def main():
	
	basicTests()


def basicTests():
	# blank
	dj = Datajack()
	print dj.hello()
	# from text
	with open('data/hello.txt') as f:
		dj2 = Datajack(f.read())
		print dj.hello
	# from file




class Datajack():
	"""Tool for creating and manipulating an EML object."""
	

	def __init__(self, text=None):
		if text == None:
			return
		if not isinstance(text, str):
			raise TypeError()
		# remove spurious whitespace e.g. final newline.
		text = text.strip()
		self.root = Element.fromString(text)


	def hello(self):
		return "world"




if __name__ == "__main__":
	main()
