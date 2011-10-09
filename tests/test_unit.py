import copy

import nose
from nose.tools import assert_equal, assert_is

from nose_sphinx_doc import SphinxDocPlugin


def test_sphinx_doc_plugin__store_test():
    """
    Test :py:meth:`nose_sphinx_doc.SphinxDocPlugin.storeTest`.
    """

    #test single call
    plugin = SphinxDocPlugin()
    test = nose.case.Test( lambda x:x)
    assert_equal(plugin.tests, [])
    plugin.storeTest(test)
    assert_equal(plugin.tests, [test])

    #test double call
    plugin = SphinxDocPlugin()
    assert_equal(plugin.tests, [])
    test1 = nose.case.Test( lambda x:x)
    test2 = nose.case.Test( lambda x:x)
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
   
