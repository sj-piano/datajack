#!/usr/bin/python


import unittest

# Initialize the test suite.
loader = unittest.TestLoader()
suite  = unittest.TestSuite()

# Add tests to the test suite.
suite.addTests(loader.discover('src/tests'))

# Initialize a runner, pass the test suite to it, and run it.
runner = unittest.TextTestRunner(verbosity=1)
result = runner.run(suite)
