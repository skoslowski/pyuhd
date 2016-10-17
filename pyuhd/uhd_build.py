import re
import os

from cffi import FFI

prefix = '/home/koslowski/.miniconda3/envs/pyuhd'
# prefix = '/opt/miniconda3/envs/pyuhd'

lines_to_exclude = re.compile(
    r'('
    r' *//|'
    r'(/| )\*| ?\*+/|'
    r'#include|'
    r'#(ifndef|define|endif) .+_H'
    r')'
)


def include_to_cdef(filename):
    lines = []
    with open(str(filename)) as fp:
        for line in fp:
            line = line.rstrip()
            if lines_to_exclude.match(line):
                continue
            line = re.sub(r'^UHD_API ', '', line)
            line = re.sub(r'^UHD_UNUSED\(([^)]*)\)', r'\1', line)
            lines.append(line)
    lines = '\n'.join(lines)

    lines = re.sub('#ifdef __cplusplus\n.*?\n#else(.*?)\n#endif', r'\1', lines, flags=re.DOTALL)
    lines = re.sub('#ifdef __cplusplus\n.*?\n#endif', r'', lines, flags=re.DOTALL)
    return lines


def show(text):
    print(*('{:4} {}'.format(i+1, line) for i, line in enumerate(text.split('\n'))), sep='\n')


include_files = [
    'error.h',
    'types/metadata.h',
    'types/tune_request.h',
    'types/tune_result.h',
    'types/ranges.h',
    'types/string_vector.h',
    'types/sensors.h',
    'types/usrp_info.h',
    'usrp/mboard_eeprom.h',
    'usrp/dboard_eeprom.h',
    'usrp/subdev_spec.h',
    'usrp/usrp.h',
]

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


ffibuilder = FFI()
ffibuilder.set_source(
    module_name='_uhd',
    source='#include <uhd.h>',
    include_dirs=[os.path.join(prefix, 'include')],
    library_dirs=[os.path.join(prefix, 'lib64'), os.path.join(prefix, 'lib')],
    libraries=['uhd'],
)
ffibuilder.cdef('typedef long time_t;')

for filename in include_files:
    filepath = os.path.join(prefix, 'include/uhd', filename)
    if __name__ == "__main__":
        print('parsing', filepath)
    csource_full = include_to_cdef(filepath)
    # show(csource)
    csource = exclude_pattern.sub('', csource_full)
    ffibuilder.cdef(csource)


if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
    # import _uhd
    # from pprint import pprint
    # pprint(dir(_uhd.lib))
