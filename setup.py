"""setuptools configuration for AuTOMate"""

from setuptools import setup, find_packages

setup(name = 'AuTOMate',
      version = '0.0.1',
      description = 'Automation server for easy Continuous Integration',
      author = 'Tom Pierce',
      author_email = 'tom.pierce0@gmail.com',
      url = 'https://github.com/tompierce/automate',
      packages = find_packages(),
      install_requires = ['flask', 'croniter', 'sh', 'pytest'],
      )
