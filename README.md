# timer.py
A context manager for timing the duration of code execution

## Usage

### Print to stdout

``` python
import timer

with timer.Timer():
    [i - 1 for i in range(10000, 9)]
# This will print in StdOut: "Executed in: 1.91 usec"

with timer.Timer('my long and important calculations'):
    [i - 1 for i in range(10000, 11)]
# This will print in StdOut: "Executed 'my long and important calculations' in: 1.19 usec"
```

### Use logging

You first need to setup logging. E.g:

``` python
import logging

logging.basicConfig(level=10)
logger = logging.getLogger()
```

and then you case use your logger object like this:

``` python
import timer

with timer.Timer('my long and important calculations', log_func=logger.warning):
    [i - 1 for i in range(10000, 13)]
# This will write to the logger handlers: "WARNING:root:Executed 'my long and important calculations' in: 0.954 usec"
```
