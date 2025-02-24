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

import txaio
txaio.use_twisted()  # noqa

import flatbuffers
import pytest
import numpy as np
from txaio import time_ns

from cfxdb.xbr import Market
from cfxdb.tests._util import _gen_ipfs_hash


def fill_market(market):
    market.market = uuid.uuid4()
    market.timestamp = np.datetime64(time_ns(), 'ns')
    market.seq = random.randint(1, 2**32 - 1)
    market.owner = os.urandom(20)
    market.coin = os.urandom(20)
    market.terms = _gen_ipfs_hash()
    market.meta = _gen_ipfs_hash()
    market.maker = os.urandom(20)
    market.provider_security = random.randint(0, 2**256 - 1)
    market.consumer_security = random.randint(0, 2**256 - 1)
    market.market_fee = random.randint(0, 2**256 - 1)
    market.tid = os.urandom(32)
    market.signature = os.urandom(65)


@pytest.fixture(scope='function')
def market():
    _market = Market()
    fill_market(_market)
    return _market


@pytest.fixture(scope='function')
def builder():
    _builder = flatbuffers.Builder(0)
    return _builder


def test_market_roundtrip(market, builder):
    # serialize to bytes (flatbuffers) from python object
    obj = market.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    assert len(data) == 544

    # create python object from bytes (flatbuffes)
    _market = Market.cast(data)

    assert _market.market == market.market
    assert _market.timestamp == market.timestamp
    assert _market.seq == market.seq
    assert _market.owner == market.owner
    assert _market.coin == market.coin
    assert _market.terms == market.terms
    assert _market.meta == market.meta
    assert _market.maker == market.maker
    assert _market.provider_security == market.provider_security
    assert _market.consumer_security == market.consumer_security
    assert _market.market_fee == market.market_fee
    assert _market.tid == market.tid
    assert _market.signature == market.signature


def test_market_roundtrip_perf(market, builder):
    obj = market.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    scratch = {'value': 0}

    def loop():
        _market = Market.cast(data)
        if True:
            assert _market.market == market.market
            assert _market.timestamp == market.timestamp
            assert _market.seq == market.seq
            assert _market.owner == market.owner
            assert _market.coin == market.coin
            assert _market.terms == market.terms
            assert _market.meta == market.meta
            assert _market.maker == market.maker
            assert _market.provider_security == market.provider_security
            assert _market.consumer_security == market.consumer_security
            assert _market.market_fee == market.market_fee
            assert _market.tid == market.tid
            assert _market.signature == market.signature

            scratch['value'] += _market.seq

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
