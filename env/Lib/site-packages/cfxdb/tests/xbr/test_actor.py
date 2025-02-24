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

from cfxdb.xbr import Actor
from cfxdb.tests._util import _gen_ipfs_hash


def fill_actor(actor):
    actor.actor = os.urandom(20)
    actor.actor_type = random.randint(1, 2)
    actor.market = uuid.uuid4()
    actor.timestamp = np.datetime64(time_ns(), 'ns')
    actor.joined = random.randint(0, 2**256 - 1)
    actor.security = random.randint(0, 2**256 - 1)
    actor.meta = _gen_ipfs_hash()
    actor.tid = os.urandom(32)
    actor.signature = os.urandom(65)


@pytest.fixture(scope='function')
def actor():
    _actor = Actor()
    fill_actor(_actor)
    return _actor


@pytest.fixture(scope='function')
def builder():
    _builder = flatbuffers.Builder(0)
    return _builder


def test_actor_roundtrip(actor, builder):
    # serialize to bytes (flatbuffers) from python object
    obj = actor.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    assert len(data) == 368

    # create python object from bytes (flatbuffes)
    _actor = Actor.cast(data)

    assert _actor.actor == actor.actor
    assert _actor.actor_type == actor.actor_type
    assert _actor.market == actor.market
    assert _actor.timestamp == actor.timestamp
    assert _actor.joined == actor.joined
    assert _actor.security == actor.security
    assert _actor.meta == actor.meta
    assert _actor.tid == actor.tid
    assert _actor.signature == actor.signature


def test_actor_roundtrip_perf(actor, builder):
    obj = actor.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    scratch = {'value': 0}

    def loop():
        _actor = Actor.cast(data)
        if True:
            assert _actor.actor == actor.actor
            assert _actor.actor_type == actor.actor_type
            assert _actor.market == actor.market
            assert _actor.timestamp == actor.timestamp
            assert _actor.joined == actor.joined
            assert _actor.security == actor.security
            assert _actor.meta == actor.meta
            assert _actor.tid == actor.tid
            assert _actor.signature == actor.signature

            scratch['value'] += _actor.actor_type

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
