from pyuhd.usrp import USRP
import numpy as np


def test():
    with USRP() as usrp:
        usrp.set_tx_rate(1.0e6)
        usrp.set_tx_freq(411e6)
        usrp.normalized_tx_gain = 0.66

        print('Frequency:', usrp.tx_freq)
        print('Gain:', usrp.tx_gain)
        print('Rate:', usrp.tx_rate)

        print('Gains:', usrp.tx_gain_names())

        streamer = usrp.get_tx_stream()
        print('Buffer size:', streamer.max_num_samps)

        buffer = np.zeros(streamer.max_num_samps, dtype='complex64')
        streamer.send([buffer], timeout=0.1, start_of_burst=True)
        streamer.send([buffer], timeout=0.1)
        streamer.send([buffer], timeout=0.1)
        streamer.send([buffer], timeout=0.1, end_of_burst=True)
        print('last error:', streamer.last_error)


if __name__ == "__main__":
    test()
