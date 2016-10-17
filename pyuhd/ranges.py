"""Classes to represent the ranges"""

from collections import namedtuple

from .uhd import ffi, lib
from .utils import CObject, cproperty


class MetaRange(CObject):
    """A range object"""
    cnamespace = 'uhd_meta_range'

    start = cproperty('double')
    stop = cproperty('double')
    step = cproperty('double')

    def clip(self, value, clip_step=True):
        result_out = ffi.new('double *')
        lib.uhd_meta_range_clip(self.handle, value, clip_step, result_out)
        return result_out[0]

    size = cproperty('size_t')

    def __len__(self):
        return self.size

    def push_back(self, start, stop=None, step=None):
        if stop is None and step is None:
            start, stop, step = start
        range_ = ffi.new('uhd_rate_t *', dict(
            start=start, stop=stop, step=step
        ))
        lib.uhd_meta_range_push_back(self.handle, range_)

    def append(self, range_):
        self.push_back(range_)

    def at(self, num):
        range_out = ffi.new('uhd_rate_t *')
        lib.uhd_meta_range_at(self.handle, num, range_out)
        result = namedtuple('Range', 'start stop step')
        return result(range_out.start, range_out.stop, range_out.step)

    def __getitem__(self, item):
        return self.at(item)

    to_pp_string = cproperty('string')
    __str__ = to_pp_string

    last_error = cproperty('string')


class StringVector(CObject):
    cnamespace = 'uhd_string_vector'

    size = cproperty('size_t')

    def __len__(self):
        return self.size

    def at(self, index):
        strbuffer_len = 400
        value = ffi.new('char[{}]'.format(strbuffer_len))
        lib.uhd_string_vector_at(self.handle, index, value, strbuffer_len)
        return ffi.string(value, strbuffer_len).decode()

    def __getitem__(self, item):
        return self.at(item)

    last_error = cproperty('string')
