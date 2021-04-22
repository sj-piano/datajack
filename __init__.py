# Imports
import logging




# Relative imports
from . import datajack




# Collect up the things that we want in the immediate namespace of the imported datajack module.
# So that from outside this package we can do e.g. datajack.Element()
Element = datajack.code.Element.Element
Entry = datajack.code.Element.Entry
validate = datajack.util.validate
configure_module_logger = datajack.util.module_logger.configure_module_logger




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
    log_filepath = None,
    ):
  # Configure logger for this module.
  datajack.util.module_logger.configure_module_logger(
    logger = logger,
    logger_name = __name__,
    log_level = log_level,
    debug = debug,
    log_timestamp = log_timestamp,
    log_filepath = log_filepath,
  )
  log('Setup complete.')
  deb('Logger is logging at debug level.')
  # Configure modules further down in this package.
  datajack.setup(
    log_level = log_level,
    debug = debug,
    log_timestamp = log_timestamp,
    log_filepath = log_filepath,
  )
