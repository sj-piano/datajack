# datajack
Tool for reading and manipulating EML (Edgecase Markup Language).


Language: Python 3.5.2

Pytest 6.1.2



### Logging approach used in this package

Disadvantages:
- Some required boilerplate for each Python file that produces log output.

Advantages:
- Each Python file has its own namespaced logger. The namespace e.g. datajack.datajack.code.Element will appear in the log line.
- log_level can be set from the cmdline when using cli.py. By default, will log at ERROR level.
- log_level can be set from the cmdline when using pytest.
- log_level will propagate down to all the loggers.

Note: During development, you may want to hardcode log levels for particular modules (or git submodules). This can be done by setting e.g. log_level='debug' or log_level='error' in the relevant setup() function.




### Validation error example


```bash
stjohn@judgement:datajack$ python3 cli.py -t valid -d
INFO     [cli: 99 (setup)] Setup complete.
DEBUG    [cli: 100 (setup)] Logger is printing debug output.
Traceback (most recent call last):
  File "cli.py", line 143, in <module>
    main()
  File "cli.py", line 78, in main
    valid(a)
  File "cli.py", line 124, in valid
    v.s(foo, 'foo', location)
  File "/mnt/c/Users/User/Desktop/stuff/hydra/repos/datajack/datajack/util/validate.py", line 201, in string
    raise TypeError(msg)
TypeError: In location 'cli.py:valid()', for variable 'foo', expected a 'string', but received value 123, which has type 'int', not 'str'.
```