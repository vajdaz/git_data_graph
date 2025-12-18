#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Allow running the package as a module:
    python -m src [options] [path]
"""

from __future__ import print_function

import sys
from .main import main

if __name__ == "__main__":
    sys.exit(main())
