#!/usr/bin/python


def main():

	print "hello world"
	dj = Datajack()
	print dj.hello()


class Datajack():
	
	def __init__(self):
		pass

	def hello(self):
		return "world"


if __name__ == "__main__":
	main()
