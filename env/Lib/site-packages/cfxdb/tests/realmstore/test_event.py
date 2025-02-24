##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################

import pytest
import random
import timeit

import flatbuffers
from txaio import with_twisted  # noqa

from txaio import time_ns
from autobahn import util
import zlmdb

from cfxdb.realmstore import Event

zlmdb.TABLES_BY_UUID = {}


def fill_event(event):
    event.timestamp = time_ns()
    event.subscription = util.id()
    event.publication = util.id()
    event.receiver = util.id()
    event.retained = random.choice([True, False])
    event.acknowledged_delivery = random.choice([True, False])


@pytest.fixture(scope='function')
def builder():
    _builder = flatbuffers.Builder(0)
    return _builder


@pytest.fixture(scope='function')
def event():
    _event = Event()
    fill_event(_event)
    return _event


def test_event_roundtrip(event, builder):
    obj = event.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    assert len(data) in [64, 56]

    _event = Event.cast(data)

    assert _event.timestamp == event.timestamp
    assert _event.subscription == event.subscription
    assert _event.publication == event.publication
    assert _event.receiver == event.receiver
    assert _event.retained == event.retained
    assert _event.acknowledged_delivery == event.acknowledged_delivery


def test_event_roundtrip_perf(event, builder):
    obj = event.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    scratch = {'timestamp': 0}

    def loop():
        _event = Event.cast(data)
        if True:
            assert _event.timestamp == event.timestamp
            assert _event.subscription == event.subscription
            assert _event.publication == event.publication
            assert _event.receiver == event.receiver
            assert _event.retained == event.retained
            assert _event.acknowledged_delivery == event.acknowledged_delivery

            scratch['timestamp'] += event.timestamp

    N = 5
    M = 100000
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
    assert scratch['timestamp'] > 0
