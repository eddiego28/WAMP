##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################

import os
import random
import timeit
import uuid

import numpy as np

import txaio
txaio.use_twisted()  # noqa

from txaio import time_ns
import flatbuffers
import pytest

from cfxdb.xbrmm import Channel


def fill_channel(channel):
    channel.market_oid = uuid.uuid4()
    channel.member_oid = uuid.uuid4()
    channel.channel_oid = uuid.uuid4()
    channel.timestamp = np.datetime64(time_ns(), 'ns')
    channel.open_at = random.randint(1, 2**256 - 1)
    channel.seq = random.randint(1, 2**32 - 1)
    channel.channel_type = random.randint(1, 2)
    channel.marketmaker = os.urandom(20)
    channel.actor = os.urandom(20)
    channel.delegate = os.urandom(20)
    channel.recipient = os.urandom(20)
    channel.amount = random.randint(1, 2**256 - 1)
    channel.timeout = random.randint(1, 2**32 - 1)
    channel.state = random.randint(1, 3)
    channel.closing_at = random.randint(1, 2**256 - 1)
    channel.closed_at = random.randint(1, 2**256 - 1)
    channel.close_mm_sig = os.urandom(65)
    channel.close_del_sig = os.urandom(65)
    channel.close_channel_seq = random.randint(1, 2**32 - 1)
    channel.close_is_final = random.choice([True, False])
    channel.close_balance = random.randint(1, 2**256 - 1)
    channel.closed_tx = os.urandom(32)


@pytest.fixture(scope='function')
def channel():
    _channel = Channel()
    fill_channel(_channel)
    return _channel


@pytest.fixture(scope='function')
def builder():
    _builder = flatbuffers.Builder(0)
    return _builder


def test_channel_roundtrip(channel, builder):
    # serialize to bytes (flatbuffers) from python object
    obj = channel.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    assert len(data) == 720

    # create python object from bytes (flatbuffes)
    _channel = Channel.cast(data)

    assert _channel.market_oid == channel.market_oid
    assert _channel.member_oid == channel.member_oid
    assert _channel.channel_oid == channel.channel_oid
    assert _channel.timestamp == channel.timestamp
    assert _channel.open_at == channel.open_at
    assert _channel.seq == channel.seq
    assert _channel.channel_type == channel.channel_type
    assert _channel.marketmaker == channel.marketmaker
    assert _channel.actor == channel.actor
    assert _channel.delegate == channel.delegate
    assert _channel.recipient == channel.recipient
    assert _channel.amount == channel.amount
    assert _channel.timeout == channel.timeout
    assert _channel.state == channel.state
    assert _channel.closing_at == channel.closing_at
    assert _channel.closed_at == channel.closed_at
    assert _channel.close_mm_sig == channel.close_mm_sig
    assert _channel.close_del_sig == channel.close_del_sig
    assert _channel.close_channel_seq == channel.close_channel_seq
    assert _channel.close_is_final == channel.close_is_final
    assert _channel.close_balance == channel.close_balance
    assert _channel.closed_tx == channel.closed_tx


def test_channel_roundtrip_perf(channel, builder):
    obj = channel.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    scratch = {'value': 0}

    def loop():
        _channel = Channel.cast(data)
        if True:
            assert _channel.market_oid == channel.market_oid
            assert _channel.member_oid == channel.member_oid
            assert _channel.channel_oid == channel.channel_oid
            assert _channel.timestamp == channel.timestamp
            assert _channel.open_at == channel.open_at
            assert _channel.seq == channel.seq
            assert _channel.channel_type == channel.channel_type
            assert _channel.marketmaker == channel.marketmaker
            assert _channel.actor == channel.actor
            assert _channel.delegate == channel.delegate
            assert _channel.recipient == channel.recipient
            assert _channel.amount == channel.amount
            assert _channel.timeout == channel.timeout
            assert _channel.state == channel.state
            assert _channel.closing_at == channel.closing_at
            assert _channel.closed_at == channel.closed_at
            assert _channel.close_mm_sig == channel.close_mm_sig
            assert _channel.close_del_sig == channel.close_del_sig
            assert _channel.close_channel_seq == channel.close_channel_seq
            assert _channel.close_is_final == channel.close_is_final
            assert _channel.close_balance == channel.close_balance
            assert _channel.closed_tx == channel.closed_tx

            scratch['value'] += int(_channel.market_oid.bytes[0])
            scratch['value'] += int(_channel.market_oid.bytes[7])
            scratch['value'] += int(_channel.market_oid.bytes[15])

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
