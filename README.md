# The Grill
[![Build Status](https://travis-ci.org/thegrill/grill.svg?branch=master)](https://travis-ci.org/thegrill/grill)
[![codecov](https://codecov.io/gh/thegrill/grill/branch/master/graph/badge.svg)](https://codecov.io/gh/thegrill/grill)
[![Documentation Status](https://readthedocs.org/projects/grill/badge/?version=latest)](https://grill.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/grill.svg)](https://badge.fury.io/py/grill)
[![PyPI](https://img.shields.io/pypi/pyversions/grill.svg)](https://pypi.python.org/pypi/grill)
---
Cook digital.

`grill` namespace, meta-package with core tools and philosophy guidelines.

With future users and readers in mind, `the grill` aims to stick to the following principles:

- [DRY (don't repeat yourself)](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself)
- [SSOT (single source of truth)](https://en.wikipedia.org/wiki/Single_source_of_truth)
- [Convention over configuration (sensible defaults)](https://en.wikipedia.org/wiki/Convention_over_configuration)
- [SOLID (understandable, flexible and maintainable)](https://en.wikipedia.org/wiki/SOLID)
- [KISS (keep it simple)](https://en.wikipedia.org/wiki/KISS_principle)

Foundational tools:
- [Python](https://docs.python.org/3/)
- [USD](https://graphics.pixar.com/usd/docs/index.html)
- [EdgeDB](https://edgedb.com)

### Install

```bash
python -m pip install grill
```

### Dependencies

The following dependencies are required and should be installed separately.

- graphviz (for graph widgets)
  ```bash
  conda install -c anaconda graphviz
  ```
- USDView (hopefully will be available soon via pypi). In the meantime, it can be downloaded from [NVidia](https://developer.nvidia.com/usd) or built from USD source ([conda recipe](https://github.com/PixarAnimationStudios/USD/issues/1260#issuecomment-656985888))