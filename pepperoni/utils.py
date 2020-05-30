"""Application utils."""


import os
import sys

py_path = os.path.abspath(sys.argv[0])
py_dir = os.path.dirname(py_path)
py_file, py_ext = os.path.splitext(os.path.basename(py_path))
