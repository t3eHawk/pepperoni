# pepperoni

Pepperoni is a toolkit for Python applications development making the process more convenient.

## Features
Pepperoni provides a set of out-of-the-box solutions:
* Logger - alternative for Python built-in logging module with similar syntax but its own way of configuration and set of unique features.
* Sysinfo - container with information from different inputs such as systems descriptors, environment variables, execution arguments, user arguments, user commands, etc.
* Credentials - generic way for access to the most secure information placed into the special configuration files from within your applications.
* Database - wrapper of fantastic SQLAlchemy, gives simple interface that allow you to connect and interract with database and its objects from within your applications using minumum code.

## Getting Started
### Requirements
Operation systems: Windows, Linux, Mac OS.

Python version: 3.8.3.

### Installation
Use pip to install the module:
```
pip install pepperoni
```

### How to Use
#### Logger
```python
import pepperoni


logger = pepperoni.logger()
```
