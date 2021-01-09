#!/usr/bin/python


import unittest


# Initialize the test suite.
loader = unittest.TestLoader()
suite  = unittest.TestSuite()

# Add tests to the test suite.
# Note: Test code is run from this file's location, so imports have to be written to run from here as well. 
suite.addTests(loader.discover('src/test'))

# Initialize a runner, pass the test suite to it, and run it.
runner = unittest.TextTestRunner(verbosity=1)
result = runner.run(suite)
