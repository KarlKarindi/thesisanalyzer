from setuptools import find_packages
from setuptools import setup

setup(
    name='ThesisAnalyzer',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask'
    ],
)
