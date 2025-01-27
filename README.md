# rustpython-ast-pyo3-wrapper

Github repository: https://github.com/hhclaw/rustpython-ast-pyo3.

## Overview

Publishes https://github.com/RustPython/rustpython-ast-pyo3, a python library
for calling the RustPython Parser from Python.

This library has enabled the "wrapper" feature, so the returned AST parse tree
will be using classes in the library rather than the Python native `ast`
class to represent the ast.  This allows parsing of code in say Python 3.11
with lower python version say Python 3.8, since some node types used in
Python 3.11 does not exist in Python 3.8's native `ast` module.

## Caveat

Due to the way the wrapper is written, objects of `static` lifetime are created
for each run. This will "leak" the ast structures created (until the end of
the Python process).  Need to be cautious if this is used within a long-running server.