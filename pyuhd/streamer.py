"""Classes to represent the streamer interfaces"""

from .uhd import ffi, lib
from .metadata import TxMetaData, RxMetaData
from .utils import CObject, cproperty


class TxStreamer(CObject):
    """A streamer for transmission"""
    cnamespace = 'uhd_tx_streamer'

    num_channels = cproperty('size_t')
    max_num_samps = cproperty('size_t')

    def send(self, buffers, timeout, **meta_data):
        """send sample data with meta data to device"""
        result = ffi.new('size_t *')
        md = meta_data.pop('meta_data', None) or TxMetaData(**meta_data)
        md_ptr = ffi.new('uhd_tx_metadata_handle*', md.handle)
        sampls_per_buff = len(buffers[0])
        buffs = ffi.new('char*[]', [ffi.from_buffer(b) for b in buffers])
        buffs = ffi.cast('void **', buffs)

        lib.uhd_tx_streamer_send(self.handle, buffs, sampls_per_buff, md_ptr,
                                 timeout, result)
        return result[0]

    def recv_async_msg(self):
        raise NotImplementedError()

    last_error = cproperty('string')


class RxStreamer(CObject):
    """A streamer for reception"""
    cnamespace = 'uhd_rx_streamer'

    num_channels = cproperty('size_t')
    max_num_samps = cproperty('size_t')

    def recv(self, buffers, timeout, one_packet, **meta_data):
        """receive sample data with meta data from the device"""

        items_recvd = ffi.new('size_t *')
        md = meta_data.pop('meta_data', None) or RxMetaData()
        md_ptr = ffi.new('uhd_tx_metadata_handle*', md.handle)
        sampls_per_buff = len(buffers[0])
        buffs = ffi.new('char*[]', [ffi.from_buffer(b) for b in buffers])
        buffs = ffi.cast('void **', buffs)

        lib.uhd_rx_streamer_recv(self.handle, buffs, sampls_per_buff, md_ptr,
                                 timeout, one_packet, items_recvd)
        return items_recvd[0]

    def issue_stream_cmd(self, stream_mode, num_samps, stream_now, full_secs, frac_secs):
        stream_cmd = ffi.new('uhd_stream_args_t*')
        for name in dir(stream_cmd):
            value = locals().get(name, None)
            if value is not None:
                setattr(stream_cmd, name, value)
        lib.uhd_rx_streamer_issue_stream_cmd(self.handle, stream_cmd)

    last_error = cproperty('string')
