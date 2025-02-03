from setuptools import setup, find_packages

packages = find_packages()
setup(
   name='spectr_reader',
   version='1.0',
   description='EMALAB Spectrometer Manager',
   packages=packages,
   install_requires=['pyepics'],
)