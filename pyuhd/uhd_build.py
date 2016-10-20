"""this builds uhd bindings using cffi"""
import re
from os import path, environ
import sys

from cffi import FFI


def find_prefix(file_to_find):
    """find a prefix based on a list of candidates and a required file"""
    candidates = [
        environ.get('UHD_PREFIX', ''),
        environ.get('UHD_DIR', ''),
        sys.prefix,
        '/usr'
        '/usr/local',
    ]
    for prefix in candidates:
        include_dir = path.join(prefix, file_to_find)
        if prefix and path.exists(include_dir):
            return prefix
    raise OSError('Missing UHD C headers. Use UHD_PREFIX to set a custom prefix')


def include_to_cdef(filename):
    """removes some pre-processor statements that the CFFI doesn't support"""
    lines = []
    with open(str(filename)) as header_file:
        for line in header_file:
            line = line.rstrip()
            if re.match(r'(#include|#(ifndef|define|endif) .+_H)', line):
                continue
            line = re.sub(r'^UHD_API ', '', line)
            line = re.sub(r'^UHD_UNUSED\(([^)]*)\)', r'\1', line)
            lines.append(line)
    cdef = '\n'.join(lines)

    cdef = re.sub('#ifdef __cplusplus\n.*?\n#else(.*?)\n#endif', r'\1', cdef, flags=re.DOTALL)
    cdef = re.sub('#ifdef __cplusplus\n.*?\n#endif', '', cdef, flags=re.DOTALL)
    return cdef


def show(text):
    """print test with line numbers"""
    print(*('{:4} {}'.format(i+1, line)
            for i, line in enumerate(text.split('\n'))), sep='\n')


include_files = [
    'include/uhd/error.h',
    'include/uhd/types/metadata.h',
    'include/uhd/types/tune_request.h',
    'include/uhd/types/tune_result.h',
    'include/uhd/types/ranges.h',
    'include/uhd/types/string_vector.h',
    'include/uhd/types/sensors.h',
    'include/uhd/types/usrp_info.h',
    'include/uhd/usrp/mboard_eeprom.h',
    'include/uhd/usrp/dboard_eeprom.h',
    'include/uhd/usrp/subdev_spec.h',
    'include/uhd/usrp/usrp.h',
]

# exclude some declaration from the generated cdefs
# --> should not need to do this....
exclude_pattern = re.compile(
    r'('
    r'uhd_error uhd_get_last_error\(.*?\);|'
    r'uhd_error uhd_usrp_set_time_source_out\([^)]*?\);|'
    r'uhd_error uhd_usrp_read_register\([^)]*?\);|'
    r'uhd_error uhd_usrp_get_rx_lo_sources\([^)]*?\);|'
    r'uhd_error uhd_usrp_get_rx_lo_names\([^)]*?\);'
    r')',
    flags=re.DOTALL
)


def get_ffi(prefix):
    ffi = FFI()
    ffi.set_source(
        module_name='_uhd',
        source='#include <uhd.h>',
        include_dirs=[path.join(prefix, 'include')],
        library_dirs=[path.join(prefix, 'lib64'), path.join(prefix, 'lib')],
        libraries=['uhd'],
    )
    ffi.cdef('typedef long time_t;')  # todo: portable?

    for filename in include_files:
        file_path = path.join(prefix, filename)
        if __name__ == "__main__":
            print('parsing', file_path)
        csource_full = include_to_cdef(file_path)
        csource = exclude_pattern.sub('', csource_full)
        # show(csource)
        ffi.cdef(csource)

    return ffi


ffibuilder = get_ffi(prefix=find_prefix(include_files[0]))

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
    # import _uhd
    # from pprint import pprint
    # pprint(dir(_uhd.lib))
