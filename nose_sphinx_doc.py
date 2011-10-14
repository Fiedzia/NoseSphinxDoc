import os
import logging
import unittest
import errno

import nose
from nose.plugins import Plugin

LOGGER = logging.getLogger(__file__)

"""
    TODO:
        * complete sphinx documentation
        * publish to pypi
        * test counter (test count in brackets next to  submodule links)
        * tests (unit and functional)
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

    def extractTestInfo(self, test):
        """
        Extract usefull information from a test.

        :param test:
            an instance of :py:class:`nose.case.Test`
        :returns:
            dictionary with fllowing keys
                * module
                    module name
                * name
                    test name
                * test
                    :py:class:`nose.case.Test` instance
                * type
                    either 'FunctionTestCase' or 'TestCase'
        """
        if isinstance(test.test, nose.case.FunctionTestCase):
            real_test = test.test.test  # get unwrapped test function
            module = real_test.__module__
            name = real_test.__name__
            return {'module': module, 'name': name,
                'test': test, 'type': 'FunctionTestCase'}

        elif isinstance(test.test, unittest.TestCase):
            module = test.test.__module__
            name = type(test.test).__name__
            return {'module': module, 'name': name,
                'test': test, 'type': 'TestCase'}
        else:
            raise Exception('unsupported test type:' + str(test.test))

    def processTests(self, tests):
        """
        Convert list of tests into a dictionary representing nested structure
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

        :param tests:
            list of istances of :py:class:`nose.case.Test`
        :returns:
            dictionary
        """
        test_dict = {}  # dict for storing test structure

        for test in tests:
            test_info = self.extractTestInfo(test)
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
        return '{0}\n{1}\n{0}\n'.format(section_char * len(name), name)

    @classmethod
    def _makedirs(cls, dirname):
        """
        Create directory structure without failing on existing dirs.

        :param dirname:
            directory name
        :raises:
            :py:exc:``OSError``
        :returns:
            None
        """
        try:
            os.makedirs(dirname)
        except OSError as exc:
            if exc.errno == errno.EEXIST:
                pass
            else:
                raise

    def _gen_header(self, module_path):
        """
        Generate header.

        :param module_path:
            list of module names
        :returns:
            text of section header
        """
        header = 'Tests'
        if module_path:
            header = '{0}'.format(module_path[-1])
        return header

    def _document_test_case(self, test_info):
        """
        Return sphinx-formatted documentation of a test case.

        Generate documentation for a :py:cls:``nose.case.TestCase``
        type of test.

        :param test_info:
            dictionary
        :returns:
            sphinx-formatted text
        """
        lines = []
        lines.append('{0}.. autoclass:: {1}.{2}\n'.format(
                ' ' * 4, test_info['module'], test_info['name']))
        lines.append('{0}:members:\n'.format(' ' * 8))
        return ''.join(lines)

    def _document_function_test_case(self, test_info):
        """
        Return sphinx-formatted documntation of a test function.

        Generate documentation for a :py:cls:``nos.case.FunctionTestCase``
        type of test.

        :param test_info:
            dictionary
        :returns:
            sphinx-formatted text
        """
        return('{0}.. autofunction:: {1}.{2}\n'.format(
            ' ' * 4, test_info['module'], test_info['name']))

    def _document_tests(self, test_info_list):
        """
        Generate sphinx section with a list of references to tests.

        :param test_info_list:
            List of ``test_info`` dictionaries
        :returns:
            sphinx-formatted documentation of test
        """
        if not test_info_list:
            return ''
        lines = []
        lines.append(self.sphinxSection('Available tests'))

        for test_info in test_info_list:
            if test_info['type'] == 'TestCase':
                lines.append(self._document_test_case(test_info))
            elif test_info['type'] == 'FunctionTestCase':
                lines.append(self._document_function_test_case(test_info))
            else:
                raise Exception('unknown test type')
        lines.append('\n')
        return ''.join(lines)

    def _get_toc(self, test_dict):
        """
        Generate TOC for submodules.
        """
        lines = []
        submodules = sorted(test_dict.keys())
        if '__tests__' in submodules:
            submodules.remove('__tests__')
        if submodules:
            lines.append('.. toctree::\n')
            lines.append('    :maxdepth: 1\n')
            lines.append('\n')
            for submodule in submodules:
                lines.append('    {0}<./{0}/index>\n'.format(submodule))
            lines.append('\n')
        return ''.join(lines)

    def _traverse(self, test_dict, dirname, module_path):
        """
        """
        self._makedirs(dirname)
        docfile = open(os.path.join(dirname, 'index.rst'), 'w')
        header = self._gen_header(module_path)

        docfile.write(self.sphinxSection(header, section_char='='))
        if module_path:
            docfile.write('    Tests in ``{0}``:\n\n'.format(
                '.'.join(module_path)))
        else:
            docfile.write('    Tests in this project:\n\n')

        docfile.write(self._get_toc(test_dict))

        if '__tests__' in test_dict:
            docfile.write(self._document_tests(test_dict['__tests__']))

        submodules = sorted(test_dict.keys())
        if '__tests__' in submodules:
            submodules.remove('__tests__')

        #recursive calls
        for m in submodules:
            new_module_path = module_path[:]
            new_module_path.append(m)
            self._traverse(test_dict[m], os.path.join(dirname, m),
                 new_module_path)
        if module_path == []:  # top-level
            if self.draw_graph:
                docfile.write(self.sphinxSection('Test graph'))
                docfile.write('.. graphviz:: tests.dot\n')

        docfile.close()

    def _drawGraph(self, test_dict, fname):
        """
        Draw graph for all tests.
        """
        def _traverse(test_dict, module_path):
            """
            """
            lines = []
            submodules = sorted(test_dict.keys())
            if '__tests__' in test_dict:
                submodules.remove('__tests__')
                for test in test_dict['__tests__']:
                    lines.append('        "{0}.{1}" [label="{1}"];\n'.format(
                        '.'.join(module_path), test['name']))
                    lines.append('        "{0}" -- "{0}.{1}";\n'.format(
                        '.'.join(module_path), test['name']))

            for submodule in submodules:
                node_id = '{0}.{1}'.format('.'.join(module_path), submodule)
                if not module_path:
                    node_id = submodule
                lines.append('        "{0}" [label="{1}"];\n'.format(
                    node_id, submodule))
                if module_path:
                    lines.append('        "{0}" -- "{0}.{1}";\n'.format(
                        '.'.join(module_path), submodule))
                new_module_path = module_path[:]
                new_module_path.append(submodule)
                lines.append(_traverse(test_dict[submodule], new_module_path))
            return ''.join(lines)

        graphfile = open(fname, 'w')

        graphfile.write('graph {\n')
        graphfile.write('    label="Tests";\n')
        graphfile.write(_traverse(test_dict, []))

        graphfile.write('}\n')

        graphfile.close()

    def genSphinxDoc(self, test_dict, dirname):
        """
        For given test_dict create nested set .rst files for sphinx.

        :param test_dict:
            python dictionary representing structure of tests

        :param: dirname:
            name of output directory
        """
        self._traverse(test_dict, dirname, [])
        if self.draw_graph:
            self._drawGraph(test_dict, os.path.join(dirname, 'tests.dot'))

    #methods inherited from Plugin

    def __init__(self, *args, **kwargs):
        super(SphinxDocPlugin, self).__init__(*args, **kwargs)
        self.tests = []  # list of all tests
        self.draw_graph = False  # draw test graph

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
                      default=env.get('NOSE_SPHINX_DOC', False),
                      help="Enable sphinx-doc: %s [NOSE_SPHINX_DOC]" %
                          (self.help()))
        parser.add_option('--sphinx-doc-dir',
                      dest='sphinx_doc_dir',
                      default=env.get('NOSE_SPHINX_DOC_DIR', '_test_doc'),
                      help="Output directory name for sphinx_doc,"
                           " use with sphinx_doc option"
                           " [NOSE_SPHINX_DOC_DIR]")
        parser.add_option('--sphinx-doc-graph',
                      action='store_true',
                      dest='sphinx_doc_graph',
                      default=env.get('NOSE_SPHINX_DOC_GRAPH', False),
                      help="Create test graph using sphinx grapviz extension,"
                           " use with sphinx_doc option"
                           " [NOSE_SPHINX_DOC_GRAPH]")

    def configure(self, options, conf):
        super(SphinxDocPlugin, self).configure(options, conf)
        self.doc_dir_name = options.sphinx_doc_dir
        self.draw_graph = options.sphinx_doc_graph

    def finalize(self, result):
        test_dict = self.processTests(self.tests)
        self.genSphinxDoc(test_dict, self.doc_dir_name)
