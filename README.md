# datajack
Tool for reading and manipulating EML (Edgecase Markup Language).


Language: Python 3.5.2

Pytest 6.1.2




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