"""Utils to make life easier"""
from collections import namedtuple

from .uhd import ffi, lib


class cproperty(property):
    """property for simple getter api calls (result as reference of last arg)"""

    def __init__(self, return_type, cfunc=None):
        self.cfunc = cfunc
        self.return_type = return_type
        getter = getattr(self, '_' + return_type + '_getter', self._default_getter)
        super().__init__(getter)

    def _default_getter(self, instance):
        result = ffi.new(self.return_type + ' *')
        self.cfunc(instance.handle, result)
        return result[0]

    def _string_getter(self, instance):
        strbuffer_len = 400
        error_out = ffi.new('char[{}]'.format(strbuffer_len))
        self.cfunc(instance.handle, error_out, strbuffer_len)
        return ffi.string(error_out, strbuffer_len).decode()

    def _time_spec_getter(self, instance):
        full_secs_out = ffi.new('time_t *')
        frac_secs_out = ffi.new('double *')
        self.cfunc(instance.handle, full_secs_out, frac_secs_out)
        result_type = namedtuple('TimeSpec', 'full_secs frac_secs')
        return result_type(full_secs_out[0], frac_secs_out[0])


class CObjectMeta(type):
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        namespace = attrs['cnamespace']
        for name, obj in attrs.items():
            if name.startswith('__'):
                continue
            if isinstance(obj, cproperty) and obj.cfunc is None:
                obj.cfunc = getattr(lib, namespace + '_' + name)


class CObject(metaclass=CObjectMeta):
    """Handles c object creating and deletion"""
    cnamespace = None

    def __init__(self, *args):
        """calls the specified make function with the args provided"""
        self._handle_owner = ffi.new(self.cnamespace + '_handle *', ffi.NULL)
        getattr(lib, self.cnamespace + '_make')(self._handle_owner, *args)

    @property
    def handle(self):
        """c handle of this object"""
        return self._handle_owner[0]

    def __del__(self):
        """free the c handle"""
        if self._handle_owner[0] != ffi.NULL:
            getattr(lib, self.cnamespace + '_free')(self._handle_owner)
            self._handle_owner[0] = ffi.NULL
