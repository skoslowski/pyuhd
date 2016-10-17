import numbers

from . import streamer, ranges
from .uhd import ffi, lib
from .utils import CObject, cproperty


class USRP(CObject):
    """represents a USRP device"""
    cnamespace = 'uhd_usrp'

    def __init__(self, *, serial=None, addr=None, resource=None, name=None, type=None,
                 vid=None, pid=None):
        """Connect to a USRP. Optionally device identifiers can be specified"""
        args = ', '.join('{}={}'.format(key, value)
                         for key, value in locals().items()
                         if key not in ('self', '__class__') and value is not None)
        super().__init__(args.encode())

    close = CObject.__del__

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    ##########################################################################
    # USRP Make / Free API calls
    ##########################################################################

    last_error = cproperty('string')

    def get_tx_stream(self, cpu_format='fc32', otw_format='sc16', args='', channels=None):
        channels = channels or [0]
        stream_args_data = dict(
            cpu_format=ffi.new("char[]", cpu_format.encode()),
            otw_format=ffi.new("char[]", otw_format.encode()),
            args=ffi.new("char[]", args.encode()),
            channel_list=ffi.new('size_t[]', channels),
            n_channels=len(channels)
        )
        stream_args = ffi.new('uhd_stream_args_t*', stream_args_data)
        tx_streamer = streamer.TxStreamer()
        lib.uhd_usrp_get_tx_stream(self.handle, stream_args, tx_streamer.handle)
        return tx_streamer

    def get_rx_stream(self, cpu_format='fc32', otw_format='sc16', args='', channels=None):
        channels = channels or [0]
        stream_args_data = dict(
            cpu_format=ffi.new("char[]", cpu_format.encode()),
            otw_format=ffi.new("char[]", otw_format.encode()),
            args=ffi.new("char[]", args.encode()),
            channel_list=ffi.new('size_t[]', channels),
            n_channels=len(channels)
        )
        stream_args = ffi.new('uhd_stream_args_t*', stream_args_data)
        rx_streamer = streamer.RxStreamer()
        lib.uhd_usrp_get_rx_stream(self.handle, stream_args, rx_streamer.handle)
        return rx_streamer

    ##########################################################################
    # multi_usrp API calls
    ##########################################################################

    # todo: add

    ##########################################################################
    # Motherboard methods
    ##########################################################################

    # todo: add

    ##########################################################################
    # EEPROM access methods
    ##########################################################################

    # todo: add

    ##########################################################################
    # RX methods
    ##########################################################################

    # todo: add

    ##########################################################################
    # TX methods
    ##########################################################################

    # todo: uhd_usrp_set_tx_subdev_spec

    num_channels = cproperty('size_t', lib.uhd_usrp_get_tx_num_channels)

    def tx_rates(self, channel):
        rates = ranges.MetaRange()
        lib.uhd_usrp_get_tx_rates(self.handle, channel, rates.handle)
        return rates

    def get_tx_rate(self, channel=0):
        result = ffi.new('double *')
        lib.uhd_usrp_get_tx_rate(self.handle, channel, result)
        return result[0]

    def set_tx_rate(self, rate, channel=0):
        lib.uhd_usrp_set_tx_rate(self.handle, rate, channel)

    tx_rate = property(get_tx_rate, set_tx_rate)

    def tx_freq_range(self, channel):
        range_ = ranges.MetaRange()
        lib.uhd_usrp_get_tx_freq_range(self.handle, channel, range_.handle)
        return range_

    def get_tx_freq(self, channel=0):
        result = ffi.new('double *')
        lib.uhd_usrp_get_tx_freq(self.handle, channel, result)
        return result[0]

    def set_tx_freq(self, freq, chan=0):
        if isinstance(freq, numbers.Number):
            request = ffi.new('uhd_tune_request_t *', dict(
                target_freq=freq,
                rf_freq_policy=lib.UHD_TUNE_REQUEST_POLICY_AUTO,
                dsp_freq_policy=lib.UHD_TUNE_REQUEST_POLICY_AUTO,
            ))
        else:
            request = freq
        result = ffi.new('uhd_tune_result_t *')
        lib.uhd_usrp_set_tx_freq(self.handle, request, chan, result)
        return result

    tx_freq = property(get_tx_freq, set_tx_freq)

    def tx_gain_names(self, channel=0):
        names = ranges.StringVector()
        lib.uhd_usrp_get_tx_gain_names(self.handle, channel, names)
        return list(names)

    def get_tx_gain(self, channel=0, name=''):
        result = ffi.new('double *')
        lib.uhd_usrp_get_tx_gain(self.handle, channel, name.encode(), result)
        return result[0]

    def set_tx_gain(self, gain, channel=0, name=''):
        lib.uhd_usrp_set_tx_gain(self.handle, gain, channel, name.encode())

    tx_gain = property(get_tx_gain, set_tx_gain)

    def get_normalized_tx_gain(self, channel=0):
        result = ffi.new('double *')
        lib.uhd_usrp_get_normalized_tx_gain(self.handle, channel, result)
        return result[0]

    def set_normalized_tx_gain(self, gain, channel=0):
        lib.uhd_usrp_set_normalized_tx_gain(self.handle, gain, channel)

    normalized_tx_gain = property(get_normalized_tx_gain,
                                  set_normalized_tx_gain)
