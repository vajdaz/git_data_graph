#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
git_data_graph - Standalone executable entry point.

This script allows running git_data_graph directly without installation:
    python git_data_graph.py [options] [path]

For nuitka compilation:
    nuitka --standalone --onefile git_data_graph.py
"""

from __future__ import print_function

import sys
import os

# Add the project root to the path so we can import src
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from src.main import main

if __name__ == "__main__":
    sys.exit(main())
