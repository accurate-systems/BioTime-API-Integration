from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in biotime_api_integration/__init__.py
from biotime_api_integration import __version__ as version

setup(
	name="biotime_api_integration",
	version=version,
	description="biotime_api_integration",
	author="biotime_api_integration",
	author_email="biotime_api_integration@",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
