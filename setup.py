import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read().strip()

VERSION = '0.1'

setup(
    name = "nose-sphinx-doc",
    version = VERSION,
    author = "Maciej Dziardziel",
    author_email = "fiedzia@gmail.com",
    description = "Generate sphinx documentation for tests.",
    long_description = read('README.rst'),
    license = 'GNU LGPL',
    url = "http://github.com/Fiedzia/NoseSphinxDoc",
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        ("License :: OSI Approved :: GNU Library or Lesser General " 
        "Public License (LGPL)"), 
        "Topic :: Software Development :: Testing",
        "Programming Language :: Python",
        ],

    py_modules = ['nose_sphinx_doc'],
    zip_safe = False,
    
    entry_points = {
        'nose.plugins': ['nose_sphinx_doc = nose_sphinx_doc:SphinxDocPlugin']
        },
    install_requires = ['nose', 'mock'],
    test_suite = 'nose.collector',
)
