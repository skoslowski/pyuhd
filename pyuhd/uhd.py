"""Wrapper module for CFFI bindings that add uhd_error checks to add API calls"""
import functools
import types

from . import _uhd


class UHDError(Exception):
    """Thrown by UHD API"""
    _by_code = {}

    def __new__(cls, *args, **kwargs):
        try:
            cls = cls._by_code[args[0]]
        except (IndexError, KeyError):
            pass
        return Exception.__new__(cls, *args, **kwargs)

    def __str__(self):
        try:
            return '{} returned error code {}'.format(*self.args)
        except IndexError:
            return str(super())

    @classmethod
    def make_subclasses(cls):
        cls._by_code.clear()
        for name in dir(_uhd.lib):
            if not name.startswith('UHD_ERROR_') or name == 'UHD_ERROR_NONE':
                continue
            cls_name = 'UHD' + name[len('UHD_ERROR_'):].title().replace('_', '') + 'Error'
            cls._by_code[getattr(_uhd.lib, name)] = type(cls_name, (cls,), {})


UHDError.make_subclasses()


def raise_on_error(uhd_func):
    """checks the return code of UHD API calls"""
    @functools.wraps(uhd_func)
    def wrapper(*args):
        code = uhd_func(*args)
        if code != _uhd.lib.UHD_ERROR_NONE:
            raise UHDError(code, uhd_func.__name__)
    return wrapper


ffi = _uhd.ffi
lib = types.ModuleType(__name__ + '.lib', doc='UHD Library with checks')
lib.__package__ = __name__

# fill the lib module with (wrapped) objects from _uhd
for item in dir(_uhd.lib):
    obj = getattr(_uhd.lib, item)
    if item.startswith('uhd_') and callable(obj):
        func = raise_on_error(obj)
    setattr(lib, item, obj)


