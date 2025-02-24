##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################

import os
import random
import timeit

from txaio import with_twisted  # noqa
import flatbuffers
import pytest
import numpy as np
from txaio import time_ns

from cfxdb.xbr import Block


def fill_block(block: Block):
    block.timestamp = np.datetime64(time_ns(), 'ns')
    block.block_number = random.randint(0, 2**256 - 1)
    block.block_hash = os.urandom(32)
    block.cnt_events = random.randint(1, 2**32 - 1)


@pytest.fixture(scope='function')
def block():
    _block = Block()
    fill_block(_block)
    return _block


@pytest.fixture(scope='function')
def builder():
    _builder = flatbuffers.Builder(0)
    return _builder


def test_block_roundtrip(block, builder):
    # serialize to bytes (flatbuffers) from python object
    obj = block.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    assert len(data) == 120

    # create python object from bytes (flatbuffes)
    _block = Block.cast(data)

    assert _block.timestamp == block.timestamp
    assert _block.block_number == block.block_number
    assert _block.block_hash == block.block_hash
    assert _block.cnt_events == block.cnt_events


def test_block_roundtrip_perf(block, builder):
    obj = block.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    scratch = {'value': 0}

    def loop():
        _block = Block.cast(data)
        if True:
            assert _block.timestamp == block.timestamp
            assert _block.block_number == block.block_number
            assert _block.block_hash == block.block_hash
            assert _block.cnt_events == block.cnt_events

            scratch['value'] += int(_block.block_hash[0])
            scratch['value'] += int(_block.block_hash[7])
            scratch['value'] += int(_block.block_hash[19])

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
