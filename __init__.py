# The real importing is done in src/__init__.py.
# This file allows an external program to do this:
# import datajack; dj = datajack.Datajack()
# Note: We can't put the import statements in here and then use
# "from . import *" in e.g. test_element.py, because then we would get
# the "Attempted relative import in non-package" error.
# (The run_tests.py script runs as a top-level module, not as a package).
from src import *
