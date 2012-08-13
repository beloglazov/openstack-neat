"""
Integration between pyqcy and other testing libraries,
especially test runners (such as unittest or nose).
"""
import mocktest

from pyqcy.properties import Property
from pyqcy.runner import run_tests


__all__ = ['TestCase']


class TestCase(mocktest.TestCase):
    """`mocktest` test case for pyqcy properties.

    Properties defined here within subclasses of :class:`TestCase`
    will be verified automatically as a part of standard `mocktest` run.
    To define them, use the typical syntax with :func:`qc` decorator::

        class Sorting(TestCase):
            '''Properties that must hold for a sorting.'''
            @qc
            def sort_preserves_length(
                l=list_(of=int, max_length=128)
            ):
                assert len(l) == len(list(sorted(l)))
            @qc
            def sort_finds_minimum(
                l=list_(of=int, min_length=1, max_length=128)
            ):
                assert min(l) == list(sorted(l))[0]

    Since :class:`TestCase` itself is a subclass of standard
    :class:`mocktest.TestCase`, it will be discovered by :func:`mocktest.main`,
    `nosetests` or similar testing utilities.
    """
    class __metaclass__(type):
        def __new__(cls, name, bases, dict_):
            """Create ``TestCase`` class that contains properties to check."""
            properties = [(k, v) for (k, v) in dict_.iteritems()
                          if isinstance(v, Property)]

            for name, prop in properties:
                test = cls._create_test_method(name, prop)
                dict_[test.__name__] = test

            return type.__new__(cls, name, bases, dict_)

        @staticmethod
        def _create_test_method(name, prop):
            """Creates a ``test_X`` method corresponding to
            given :class:`Property`.

            :param name: Name of the property
            :param prop: :class:`Property` object
            :return: Test method
            """
            def test(self):
                run_tests([prop], verbosity=0, propagate_exc=True)

            test.__name__ = "test_%s" % name
            test.__doc__ = "[pyqcy] %s" % name

            return test
