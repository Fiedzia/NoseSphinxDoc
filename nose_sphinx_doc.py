import os
import logging
import types
import unittest
import errno 

import nose
from nose.plugins import Plugin

LOGGER = logging.getLogger(__file__)

"""
    TODO:
        * complete sphinx documentation
        * prepare nose plugin
        * test counter (test count in brackets next to  submodule links)
        * tests (unit and functional)
        * graphviz graphs
"""

class SphinxDocPlugin(Plugin):
    """
    Generate documentation of tests in sphinx rest format.

    Create documentation of tests, in a form of a
    sphinx .rst file with references to all tests.
    """

    name = 'sphinx_doc'
    """plugin name"""
    enableOpt = 'sphinx_doc'
    """default name for ouput file"""

    #custom methods of SphinxDocPlugin

    def storeTest(self, test):
        """
        Add test to list of tests stored in self.tests.

        :param test:
            an instance of :py:class:`nose.case.Test`
        """
        self.tests.append(test)

    def testToDict(self, test_dict, test_info):
        """
        For given test create proper entries in test_dict.

        :param test_info:
            python dictionary with information about a test,
            contains keys:
            * module: module name
            * name: test name
            * test: an instance of :py:class:`nose.case.Test`
            * type: either "FunctionTestCase" or "TestCase"
        :param test_dict:
            python dictionary, will be modified
        """
        modules = test_info['module'].split('.')
        current = test_dict
        for submodule in modules:
            if submodule in current:
                pass
            else:
                current[submodule] = {}
            current = current[submodule]
        if '__tests__' in current:
            current['__tests__'].append(test_info)
        else:
            current['__tests__'] = [test_info]

    def processTests(self, tests):
        """
        Convert list of tests stored in self.tests into
        a dictionary representing nested structure
        of tests.

        For example for given module structure:

        .. code-block :: none

            top_level_module
                -> sub_module
                    -> def test_me() ...
                    -> class MyTest(TestCase) ...


        result will look like this:

        .. code-block :: javascript

            {
                'top_level_module': {
                    'sub_module': {
                        '__tests__: {
                            'test_me': ,
                            'MyTest': ,
                         }
                    }
            }
        """
        test_list = []  # list of tuples (module, name, test)
        test_dict = {}  # dict for storing test structure

        for test in tests:

            if isinstance(test.test, nose.case.FunctionTestCase):
                real_test = test.test.test  # get unwrapped test function
                module = real_test.__module__
                name = real_test.__name__
                test_list.append({'module': module, 'name': name,
                    'test': test, 'type': 'FunctionTestCase'})

            elif issubclass(type(test.test), unittest.TestCase):
                module = test.test.__module__
                name = type(test.test).__name__
                test_list.append({'module': module, 'name': name,
                    'test': test, 'type': 'TestCase'})
            else:
                raise Exception('unsupported test type:' + str(test.test))

        for test_info in test_list:
            self.testToDict(test_dict, test_info)
        return test_dict


    def sphinxSection(self, name, section_char='-'):
        """
        Generate sphinx-formatted header.

        :param name:
            Section name
        :param section_char:
            character used for marging section type
        :returns:
            Sphinx section header.
        """
        return '{0}\n{1}\n{0}\n'.format(section_char*len(name), name)


    def genSphinxDoc(self, test_dict, dirname):
        """
        For given test_dict create nested set .rst files for sphinx.
        
        :param test_dict:
            python dictionary representing structure of tests

        :param: dirname:
            name of output directory
        """

            

        def _traverse(test_dict, dirname, module_path):
            """
            """
            try:
                os.makedirs(dirname)
            except OSError as exc:
                if exc.errno == errno.EEXIST:
                    pass
                else:
                    raise
            docfile = open(os.path.join(dirname, 'index.rst'), 'w')

            header = 'Tests'
            if module_path:
                header = 'Tests for {0}'.format('.'.join(module_path))

            docfile.write(self.sphinxSection(header, section_char='='))


            if '__tests__' in test_dict:
                docfile.write(self.sphinxSection('Available tests'))

                for test_info in test_dict['__tests__']:
                    if test_info['type'] == 'TestCase':
                        docfile.write(
                             '{0}.. autoclass:: {1}.{2}\n'.format(
                                ' ' * 4, test_info['module'],
                                test_info['name']))
                        docfile.write('{0}:members:\n'.format(' '*8))
                    elif test_info['type'] == 'FunctionTestCase':
                        docfile.write('{0}.. autofunction:: {1}.{2}\n'
                            .format(' ' * 4, test_info['module'],
                             test_info['name']))
                docfile.write('\n')

            submodules = sorted(test_dict.keys())
            if '__tests__' in submodules:
                submodules.remove('__tests__')
            if submodules:
                docfile.write(self.sphinxSection('Submodules'))
            for m in submodules:
                    docfile.write('{0}:doc:`./{1}/index.rst`\n'.format(' ' * 4, m))
            docfile.close()

            #recursive calls
            for m in submodules:
                new_module_path = module_path[:]
                new_module_path.append(m)
                _traverse(test_dict[m], os.path.join(dirname, m) , new_module_path)

        _traverse(test_dict, dirname, [])

    #methods inherited from Plugin

    def __init__(self, *args, **kwargs):
        super(SphinxDocPlugin, self).__init__(*args, **kwargs)
        self.tests = []  # list of all tests

    def prepareTestCase(self, test):
        self.storeTest(test)

    def begin(self):
        pass

    def options(self, parser, env=os.environ):
        #skip super call to avoid adding --with-* option.
        #super(SphinxDocPlugin, self).options(parser, env=env)
        parser.add_option('--sphinx-doc',
                          action='store_true',
                          dest=self.enableOpt,
                          default=env.get('NOSE_SPHINX_DOC'),
                          help="Enable sphinx-doc: %s [NOSE_SPHINX_DOC]" %
                              (self.help()))
        parser.add_option('--sphinx-doc-dir',
                          dest='sphinx_doc_dir',
                          default=env.get('NOSE_SPHINX_DOC_DIR', '_test_doc'),
                          help="Output directory name for sphinx_doc,"
                               " use with sphinx_doc option"
                               " [NOSE_SPHINX_DOC_DIR]")


    def configure(self, options, conf):
        super(SphinxDocPlugin, self).configure(options, conf)
        self.doc_dir_name = options.sphinx_doc_dir

    def finalize(self, result):
        test_dict = self.processTests(self.tests)
        self.genSphinxDoc(test_dict, self.doc_dir_name)

