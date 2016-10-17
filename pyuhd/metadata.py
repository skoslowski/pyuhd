from .utils import CObject, cproperty


class TxMetaData(CObject):
    """tx metadata"""
    cnamespace = 'uhd_tx_metadata'

    def __init__(self, has_time_spec=False, full_secs=0, frac_secs=0.0,
                 start_of_burst=False, end_of_burst=False):
        """create metadata object"""
        super().__init__(has_time_spec, full_secs, frac_secs, start_of_burst, end_of_burst)

    has_time_spec = cproperty('bool')
    time_spec = cproperty('time_spec')
    start_of_burst = cproperty('bool')
    end_of_burst = cproperty('bool')
    last_error = cproperty('string')


class RxMetaData(CObject):
    """rx metadata"""
    cnamespace = 'uhd_rx_metadata'

    has_time_spec = cproperty('bool')
    time_spec = cproperty('time_spec')

    more_fragments = cproperty('bool')
    fragment_offset = cproperty('size_t')

    start_of_burst = cproperty('bool')
    end_of_burst = cproperty('bool')

    out_of_sequence = cproperty('bool')

    to_pp_string = cproperty('string')
    __str__ = to_pp_string

    strerror = cproperty('string')
    last_error = cproperty('string')


class AsyncMetaData(CObject):
    """async metadata"""
    cnamespace = 'uhd_async_metadata'

    channel = cproperty('size_t')
    has_time_spec = cproperty('bool')
    time_spec = cproperty('time_spec')
    event_code = cproperty('size_t')
    user_payload = cproperty('uhd_async_metadata_event_code_t')
    last_error = cproperty('string')
