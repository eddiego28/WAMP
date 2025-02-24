##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################

import random
import timeit

import txaio
txaio.use_twisted()  # noqa

import flatbuffers
import pytest

from cfxdb.xbrmm import ChannelBalance


def fill_channel_balance(channel_balance):
    channel_balance.remaining = random.randint(0, 2**256 - 1)
    channel_balance.inflight = random.randint(0, 2**256 - 1)
    channel_balance.seq = random.randint(0, 2**32 - 1)


@pytest.fixture(scope='function')
def channel_balance():
    _channel_balance = ChannelBalance()
    fill_channel_balance(_channel_balance)
    return _channel_balance


@pytest.fixture(scope='function')
def builder():
    _builder = flatbuffers.Builder(0)
    return _builder


def test_channel_balance_roundtrip(channel_balance, builder):
    # serialize to bytes (flatbuffers) from python object
    obj = channel_balance.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    assert len(data) == 112

    # create python object from bytes (flatbuffes)
    _channel_balance = ChannelBalance.cast(data)

    assert _channel_balance.remaining == channel_balance.remaining
    assert _channel_balance.inflight == channel_balance.inflight
    assert _channel_balance.seq == channel_balance.seq


def test_channel_balance_roundtrip_perf(channel_balance, builder):
    obj = channel_balance.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    scratch = {'value': 0}

    def loop():
        _channel_balance = ChannelBalance.cast(data)
        if True:
            assert _channel_balance.remaining == channel_balance.remaining
            assert _channel_balance.inflight == channel_balance.inflight
            assert _channel_balance.seq == channel_balance.seq

            scratch['value'] += int(_channel_balance.seq)

    N = 5
    M = 10000
    samples = []
    print('measuring:')
    for i in range(N):
        secs = timeit.timeit(loop, number=M)
        ops = round(float(M) / secs, 1)
        samples.append(ops)
        print('{} objects/sec performance'.format(ops))

    samples = sorted(samples)
    ops50 = samples[int(len(samples) / 2)]
    print('RESULT: {} objects/sec median performance'.format(ops50))

    assert ops50 > 1000
    print(scratch['value'])
