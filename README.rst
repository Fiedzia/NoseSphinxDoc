=============
NoseSphinxDoc
=============

------------
Introduction
------------

Nose plugin that will generate sphinx-formatted test documentation.

With this nose plugin you can easily automate generation of sphinx documentation
for your tests. NoseSphinxDoc will create set of .rst files with proper references to tests,
reflecting structure of your modules.


------------
Installation
------------

    ::

    pip install --upgrade "git+git://github.com/Fiedzia/NoseSphinxDoc.git#egg=Fiedzia"

-----
Usage
-----



Basically::

    nosetests --sphinx-doc --sphinx-doc-dir=/path/to/sphinx/doc/subdirectory

For example, if you have your existing sphinx documentation in ./doc directory,
actuall call will look like this::

    nosetests --sphinx-doc --sphinx-doc-dir=./doc/tests

This will create ./doc/tests directory, containing generated documentation.
In order to link generated documentation you will need to reference
./doc/tests/index.rst file somewhere in your documentation.
Top level index.rst is a good place to do that.

NoseSphinxDoc does not require test to actually be run, its should happily work with
collect-only plugin, so you can run nose to document all tests, and then run it again
and execute only subset of them.


If you use ``--sphinx-doc-graph`` option, graph.rst file will be created,
with a simple drawing of your tests structure. This requires ``sphinx.ext.graphviz``
to be added to sphinx extension list.

