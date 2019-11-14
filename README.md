# pepperoni

Pepperoni is an alternative for Python built-in logging module.
It has similar syntax but at the same time allow you to create more elegant,
large and extendible logs for you applications.

Also Pepperoni is a toolkit making your development easier and faster.

## Features
Pepperoni loggers provide a set of out-of-the-box solutions:
- All methods to create, customize and support your logs.
- Writing to the console, file, database, email.
- Automatic alarm sending to your email in case of registered error.
- Easy way to read and configure execution arguments of different types.
- Gathered statistics including a lot of system parameters, environment
  variables, parameters from file and so on.

## Getting Started
### Requirements
Operation systems: Windows, Linux, Mac OS.

Python version: 3.7.1.

### Installation
Use pip to install the module:
```
pip install pepperoni
```

### How to Use
To start just call the logger:
```python
import pepperoni


logger = pepperoni.logger()
```
