##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################

import os
import random
import timeit

import txaio
txaio.use_twisted()  # noqa

import flatbuffers
import pytest

from cfxdb.xbr import TokenTransfer


def fill_token_transfer(token_transfer):
    token_transfer.tx_hash = os.urandom(32)
    token_transfer.block_hash = os.urandom(32)
    token_transfer.from_address = os.urandom(20)
    token_transfer.to_address = os.urandom(20)
    token_transfer.value = random.randint(1, 2**256 - 1)


@pytest.fixture(scope='function')
def token_transfer():
    _token_transfer = TokenTransfer()
    fill_token_transfer(_token_transfer)
    return _token_transfer


@pytest.fixture(scope='function')
def builder():
    _builder = flatbuffers.Builder(0)
    return _builder


def test_token_transfer_roundtrip(token_transfer, builder):
    # serialize to bytes (flatbuffers) from python object
    obj = token_transfer.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    assert len(data) == 220

    # create python object from bytes (flatbuffes)
    _token_transfer = TokenTransfer.cast(data)

    assert _token_transfer.tx_hash == token_transfer.tx_hash
    assert _token_transfer.block_hash == token_transfer.block_hash
    assert _token_transfer.from_address == token_transfer.from_address
    assert _token_transfer.to_address == token_transfer.to_address
    assert _token_transfer.value == token_transfer.value


def test_token_transfer_roundtrip_perf(token_transfer, builder):
    obj = token_transfer.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    scratch = {'value': 0}

    def loop():
        _token_transfer = TokenTransfer.cast(data)
        if True:
            assert _token_transfer.tx_hash == token_transfer.tx_hash
            assert _token_transfer.block_hash == token_transfer.block_hash
            assert _token_transfer.from_address == token_transfer.from_address
            assert _token_transfer.to_address == token_transfer.to_address
            assert _token_transfer.value == token_transfer.value

            scratch['value'] += int(_token_transfer.tx_hash[0])
            scratch['value'] += int(_token_transfer.tx_hash[7])
            scratch['value'] += int(_token_transfer.tx_hash[19])

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
