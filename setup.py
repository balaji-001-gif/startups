from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in startup_os/__init__.py
from startup_os import __version__ as version

setup(
	name="startup_os",
	version=version,
	description="The all-in-one Frappe/ERPNext custom application for Indian Startups",
	author="Balaji",
	author_email="support@startupos.in",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
