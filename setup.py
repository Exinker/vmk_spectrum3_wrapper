from setuptools import find_packages, setup

from vmk_spectrum3_wrapper import AUTHOR_EMAIL, AUTHOR_NAME, DESCRIPTION, NAME, VERSION


setup(
    # info
    name=NAME,
    description=DESCRIPTION,
    license='MIT',
    keywords=['spectroscopy', 'emulation'],

    # version
    version=VERSION,

    # author details
    author=AUTHOR_NAME,
    author_email=AUTHOR_EMAIL,

    # setup directories
    packages=find_packages(),

    # setup data
    include_package_data=True,

    # requires
    install_requires=[
        item.strip() for item in open('requirements.txt', 'r').readlines()
        if item.strip()
    ],
    python_requires='>=3.10',

)
