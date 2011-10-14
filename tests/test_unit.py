import copy
import unittest
import errno

import nose
from nose.tools import assert_equal, assert_raises
from mock import Mock, patch

from nose_sphinx_doc import SphinxDocPlugin


def _get_test_case_mock(module_name='module'):
    """
    Return mock of an instance of :py:class:`nose.case.Test`.
    """
    test = Mock(nose.case.Test)
    test.test = Mock(unittest.TestCase)
    test.test.__module__ = module_name
    return test


def _get_function_test_case_mock(module_name='module'):
    """
    Return mock of an instance of :py:class:`nose.case.Test`.
    """
    test = Mock(nose.case.Test)
    test.test = Mock(unittest.TestCase)
    test.test.__module__ = module_name
    return test


def _get_test_case_info_mock():
    """
    Return mock of test_info structure
    """
    test_info = {
        'name': 'test_me',
        'module': 'module',
        'test': _get_test_case_mock(),
        'type': 'TestCase',
    }
    return test_info


def _get_function_test_case_info_mock():
    """
    Return mock of test_info structure
    """
    test_info = {
        'name': 'test_me',
        'module': 'module',
        'test': _get_function_test_case_mock(),
        'type': 'FunctionTestCase',
    }
    return test_info


def test_sphinx_doc_plugin__store_test__single_call():
    """
    Test single call of :py:meth:`.SphinxDocPlugin.storeTest`.
    """
    #test single call
    plugin = SphinxDocPlugin()
    test = nose.case.Test(lambda x: x)
    assert_equal(plugin.tests, [])
    plugin.storeTest(test)
    assert_equal(plugin.tests, [test])


def test_sphinx_doc_plugin__store_test__several_calls():
    """
    Test several calls to :py:meth:`.SphinxDocPlugin.storeTest`.
    """
    #test double call
    plugin = SphinxDocPlugin()
    assert_equal(plugin.tests, [])
    test1 = nose.case.Test(lambda x: x)
    test2 = nose.case.Test(lambda x: x)
    plugin.storeTest(test1)
    plugin.storeTest(test2)
    assert_equal(plugin.tests, [test1, test2])


def test_sphinx_doc_plugin__test_to_dict():
    """
    Test :py:meth:`nose_sphinx_doc.SphinxDocPlugin.testToDict`.
    """
    plugin = SphinxDocPlugin()
    test_info = {
        'module': 'sample',
        'name': 'test_sample',
        'test': None,
        'type': 'FunctionTestCase'
    }
    expected_info = copy.deepcopy(test_info)
    expected_dict = {
        'sample': {
            '__tests__': [expected_info]
        }
    }
    test_dict = {}
    plugin.testToDict(test_dict, test_info)
    assert_equal(test_dict, expected_dict)


def test_sphinx_doc_plugin__extract_test_info__function():
    """
    Test test data extraction from FunctionTestCase.

    Test :py:meth:`.SphinxDocPlugin.extractTestInfo` for proper info extraction
    from an instance of :py:class:`nose.case.FunctionTestCase`.
    """
    plugin = SphinxDocPlugin()
    test = Mock(nose.case.Test)
    test.test = Mock(nose.case.FunctionTestCase)
    test.test.test = Mock()
    test.test.test.__module__ = 'module'
    test.test.test.__name__ = 'name'

    expected_result = {
        'module': 'module',
        'name': 'name',
        'test': test,
        'type': 'FunctionTestCase',
    }
    test_info = plugin.extractTestInfo(test)
    assert_equal(test_info, expected_result)


def test_sphinx_doc_plugin__extract_test_info__test_case():
    """
    Test test data extraction from unittest.TestCase.

    Test :py:meth:`.SphinxDocPlugin.extractTestInfo` for proper info extraction
    from an instance of :py:class:`unittest.TestCase`.
    """
    plugin = SphinxDocPlugin()
    test = Mock(nose.case.Test)
    test.test = Mock(unittest.TestCase)
    test.test.__module__ = 'module'

    expected_result = {
        'module': 'module',
        'name': 'Mock',
        'test': test,
        'type': 'TestCase',
    }
    test_info = plugin.extractTestInfo(test)
    assert_equal(test_info, expected_result)


def test_sphinx_doc_plugin__extract_test_info__unsupported_type():
    """
    Test  proper exception raising for unsupported data types.

    Test :py:meth:`.SphinxDocPlugin.extractTestInfo` for proper exception
    raising for unsupported types of tests.
    """
    class Dummy:
        pass
    plugin = SphinxDocPlugin()
    test = Mock(nose.case.Test)
    test.test = Mock(Dummy)
    test.test.test = Mock()
    test.test.__module__ = 'module'

    assert_raises(Exception, plugin.extractTestInfo, test)


@patch('nose_sphinx_doc.SphinxDocPlugin.testToDict')
@patch('nose_sphinx_doc.SphinxDocPlugin.extractTestInfo')
def test_sphinx_doc_plugin__process_tests__empty_list(extractTestInfo,
                                                        testToDict):
    """
    Test :py:meth:`.SphinxDocPlugin.processTests` with empty list.
    """
    plugin = SphinxDocPlugin()
    test_list = []
    expected_result = {}
    result = plugin.processTests(test_list)
    assert_equal(result, expected_result)
    assert_equal(extractTestInfo.call_count, 0)
    assert_equal(testToDict.call_count, 0)


@patch('nose_sphinx_doc.SphinxDocPlugin.testToDict')
@patch('nose_sphinx_doc.SphinxDocPlugin.extractTestInfo')
def test_sphinx_doc_plugin__process_tests__single_test(extractTestInfo,
                                                        testToDict):
    """
    Test :py:meth:`.SphinxDocPlugin.processTests` with single test.
    """
    plugin = SphinxDocPlugin()
    test_list = [1]
    expected_result = {}
    result = plugin.processTests(test_list)
    assert_equal(result, expected_result)
    assert_equal(extractTestInfo.call_count, 1)
    assert_equal(testToDict.call_count, 1)


@patch('nose_sphinx_doc.SphinxDocPlugin.testToDict')
@patch('nose_sphinx_doc.SphinxDocPlugin.extractTestInfo')
def test_sphinx_doc_plugin__process_tests__several_tests(extractTestInfo,
                                                        testToDict):
    """
    Test :py:meth:`.SphinxDocPlugin.processTests` with several test.
    """
    plugin = SphinxDocPlugin()
    test_list = [1, 2, 3]
    expected_result = {}
    result = plugin.processTests(test_list)
    assert_equal(result, expected_result)
    assert_equal(extractTestInfo.call_count, len(test_list))
    assert_equal(testToDict.call_count, len(test_list))


def test_sphinx_doc_plugin__process_tests_sphinx_section():
    """
    Test :py:meth:`.SphinxDocPlugin.sphinxSection`.
    """
    plugin = SphinxDocPlugin()
    expected_result = '-----\nTests\n-----\n'
    result = plugin.sphinxSection('Tests')
    assert_equal(result, expected_result)

    expected_result = '=====\nTests\n=====\n'
    result = plugin.sphinxSection('Tests', section_char='=')
    assert_equal(result, expected_result)


@patch('nose_sphinx_doc.os')
def test_sphinx_doc_plugin___makedirs_success(os_mock):
    """
    Test :py:meth:`.SphinxDocPlugin._makedirs`.
    """
    SphinxDocPlugin._makedirs('/a/b/c/d')
    assert_equal(os_mock.makedirs.call_count, 1)
    assert_equal(os_mock.makedirs.call_args, (('/a/b/c/d',), {}))


@patch('nose_sphinx_doc.os')
def test_sphinx_doc_plugin___makedirs_existing_dir(os_mock):
    """
    Test :py:meth:`.SphinxDocPlugin._makedirs` for existing dir.
    """
    os_mock.makedirs.side_effect = OSError()
    os_mock.makedirs.side_effect.errno = errno.EEXIST
    SphinxDocPlugin._makedirs('/a/b/c/d')


@patch('nose_sphinx_doc.os')
def test_sphinx_doc_plugin___makedirs_exception(os_mock):
    """
    Test :py:meth:`.SphinxDocPlugin._makedirs` for exception raising.
    """
    os_mock.makedirs.side_effect = OSError()
    assert_raises(OSError, SphinxDocPlugin._makedirs, '/a/b/c/d')


def test_sphinx_doc_plugin___gen_header():
    """
    Test :py:meth:`.SphinxDocPlugin._gen_header`.
    """
    plugin = SphinxDocPlugin()
    assert_equal(plugin._gen_header([]), 'Tests')
    assert_equal(plugin._gen_header(['mod1', 'mod2']), 'mod2')


def test_sphinx_doc_plugin___document_test_case():
    """
    Test :py:meth:`.SphinxDocPlugin._document_test_case`.
    """
    plugin = SphinxDocPlugin()
    test_info = {
        'name': 'test_me',
        'module': 'module',
        'test': _get_test_case_mock(),
        'type': 'TestCase',
    }
    expected = '    .. autoclass:: module.test_me\n        :members:\n'
    assert_equal(plugin._document_test_case(test_info), expected)


def test_sphinx_doc_plugin___document_function_test_case():
    """
    Test :py:meth:`.SphinxDocPlugin._document_funtion_test_case`.
    """
    plugin = SphinxDocPlugin()
    test_info = {
        'name': 'test_me',
        'module': 'module',
        'test': _get_test_case_mock(),
        'type': 'FunctionTestCase',
    }
    expected = '    .. autofunction:: module.test_me\n'
    assert_equal(plugin._document_function_test_case(test_info), expected)


def test_sphinx_doc_plugin___document_tests__empty():
    """
    Test :py:meth:`.SphinxDocPlugin._document_tests` with empty list of tests.
    """
    plugin = SphinxDocPlugin()
    plugin.sphinxSection = Mock()
    result = plugin._document_tests([])
    expected = ''
    assert_equal(result, expected)
    assert_equal(plugin.sphinxSection.call_count, 0)


def test_sphinx_doc_plugin___document_tests__test_case():
    """
    Test :py:meth:`.SphinxDocPlugin._document_tests`` with a ``TestCase``.

    Test :py:meth:`.SphinxDocPlugin._document_tests` with an instance of
    :py:cls:``nose.case.TestCase``.
    """
    plugin = SphinxDocPlugin()
    plugin.sphinxSection = Mock(return_value='')
    plugin._document_test_case = Mock(return_value='')
    result = plugin._document_tests([_get_test_case_info_mock()])
    #expect only \n, as section and test docs are mocked to return ''
    expected = '\n'
    assert_equal(result, expected)
    assert_equal(plugin.sphinxSection.call_count, 1)


def test_sphinx_doc_plugin___document_tests__function_test_case():
    """
    Test ``SphinxDocPlugin._document_tests`` with a ``FunctionTestCase``.

    Test :py:meth:`.SphinxDocPlugin._document_tests` with an instance of
    :py:cls:``nose.case.FunctionTestCase``.
    """
    plugin = SphinxDocPlugin()
    plugin.sphinxSection = Mock(return_value='')
    plugin._document_function_test_case = Mock(return_value='')
    result = plugin._document_tests([_get_function_test_case_info_mock()])
    #expect only \n, as section and test docs are mocked to return ''
    expected = '\n'
    assert_equal(result, expected)
    assert_equal(plugin.sphinxSection.call_count, 1)
