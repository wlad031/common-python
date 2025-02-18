from setuptools import setup, find_packages

setup(
    name="common_python",
    version="0.2.0",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        'Flask',
        'PyYAML',
    ],
    author='Vladislav Gerasimov',
    author_email='me@vgerasimov.dev',
    description='Common utilities for my Python projects',
    url='https://github.com/wlad031/common-python',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
)

