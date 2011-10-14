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

For example, if you have your existing sphinx documentation in ./docs directory,
actuall call will look like this::

    nosetests --sphinx-doc --sphinx-doc-dir=./docs/tests

This will create ./docs/tests directory, containing generated documentation.
In order to link generated documentation you will need to reference
./doc/tests/index.rst file somewhere in your documentation.
Top level index.rst is a good place to do that.

NoseSphinxDoc does not require test to actually be run, its should happily work with
collect-only plugin, so you can run nose to document all tests quickly,
and then run it again to execute only chosen subset.

If you use ``--sphinx-doc-graph`` option, a graph will be created,
with a simple drawing of your tests structure. This requires ``sphinx.ext.graphviz``
to be added to sphinx extension list.

If it works for you, please let me know, i'd like to hear that i'v made something useful.

---------
Debugging
---------

If something doesn't work:

    * Make sure that nose runs succesfully without any plugins. If nose
      will fail (you will see a failure information in nose output)
      then so will everything else and you will have to fix this problem first.
      If you are using several plugins, turn them on one by one,
      to find the culprit.

    * Look at ``PYTHONPATH``. You may need to set it properly for nose
      and for sphinx, as they both will need to look at python code the same way.
      Forcing them to do so is sometimes tricky, and nose can communicate errors
      really poorly.

    * If everything still fails, go to NoseSphinxDoc github page and create an issue,
      providing all details and minimal code that lead to an error.
