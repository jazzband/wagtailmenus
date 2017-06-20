import inspect
import sys

"""
This method below was copied from wagtail.wagtailcore.utils (v1.11) and allows
us to handle deprecation of method arguments in a way that doesn't swallow
`TypeError` exceptions raised further down the chain. Thank you @gasman!
"""


def accepts_kwarg(func, kwarg):
    """
    Determine whether the callable `func` has a signature that accepts the
    keyword argument `kwarg`
    """
    if sys.version_info >= (3, 3):
        signature = inspect.signature(func)
        try:
            signature.bind_partial(**{kwarg: None})
            return True
        except TypeError:
            return False
    else:
        # Fall back on inspect.getargspec, available on Python 2.7 but
        # deprecated since 3.5
        argspec = inspect.getargspec(func)
        return (kwarg in argspec.args) or (argspec.keywords is not None)
