# PyoFormats
Simple wrapper for python-formats
---
## Example
```python
from pyoformats import read

# displays names and shapes of all available series in file
read.file_info("test.msr")

# returns 5d numpy array of image in series
read.image_5d("test.msr", series=1)
```

## Installation

1. git clone <this-repo>
2. `cd pyoformats`
3. pip install -e .

## Dependencies
* numpy
* javabridge
* python-bioformats

