##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################

import pytest
import os
import random
import uuid
import timeit
import platform

import flatbuffers
from txaio import with_twisted  # noqa

from txaio import time_ns
from autobahn import util
import zlmdb

from cfxdb.realmstore import Publication

zlmdb.TABLES_BY_UUID = {}


@pytest.fixture(scope='function')
def builder():
    _builder = flatbuffers.Builder(0)
    return _builder


def fill_publication(publication):

    publication.timestamp = time_ns()
    publication.publication = util.id()
    publication.publisher = util.id()
    publication.topic = 'com.example.foobar.{}.doit'.format(uuid.uuid4())

    publication.args = [23, 'hello', {'foo': 0.5}]
    publication.kwargs = {'bar': 23, 'baz': [1, 2, 3]}
    publication.payload = os.urandom(32)

    publication.acknowledge = random.choice([True, False])
    publication.retain = random.choice([True, False])
    publication.exclude_me = random.choice([True, False])

    i0 = util.id()
    publication.exclude = [i0 + j + 1000 for j in range(5)]
    publication.exclude_authid = ['user1', 'user2', 'user3']
    publication.exclude_authrole = ['roleA', 'roleB', 'roleC']

    i0 = util.id()
    publication.eligible = [i0 + j + 1000 for j in range(5)]
    publication.eligible_authid = ['user4', 'user5', 'user6']
    publication.eligible_authrole = ['roleD', 'roleE', 'roleF']

    publication.enc_algo = Publication.ENC_ALGO_XBR
    publication.enc_key = os.urandom(32)
    publication.enc_serializer = Publication.ENC_SER_CBOR


@pytest.fixture(scope='function')
def publication():
    _publication = Publication()
    fill_publication(_publication)
    return _publication


def test_publication_roundtrip(publication, builder):
    obj = publication.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    assert len(data) in [624, 632, 640]

    _publication = Publication.cast(data)

    assert _publication.timestamp == publication.timestamp
    assert _publication.publication == publication.publication
    assert _publication.publisher == publication.publisher
    assert _publication.topic == publication.topic
    assert _publication.args == publication.args
    assert _publication.kwargs == publication.kwargs
    assert _publication.payload == publication.payload
    assert _publication.acknowledge == publication.acknowledge
    assert _publication.retain == publication.retain
    assert _publication.exclude_me == publication.exclude_me
    assert _publication.exclude == publication.exclude
    assert _publication.exclude_authid == publication.exclude_authid
    assert _publication.exclude_authrole == publication.exclude_authrole
    assert _publication.eligible == publication.eligible
    assert _publication.eligible_authid == publication.eligible_authid
    assert _publication.eligible_authrole == publication.eligible_authrole
    assert _publication.enc_algo == publication.enc_algo
    assert _publication.enc_key == publication.enc_key
    assert _publication.enc_serializer == publication.enc_serializer


def test_publication_roundtrip_perf(publication, builder):
    obj = publication.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    scratch = {'timestamp': 0}

    def loop():
        _publication = Publication.cast(data)
        if True:
            assert _publication.timestamp == publication.timestamp
            assert _publication.publication == publication.publication
            assert _publication.publisher == publication.publisher
            assert _publication.topic == publication.topic
            assert _publication.args == publication.args
            assert _publication.kwargs == publication.kwargs
            assert _publication.payload == publication.payload
            assert _publication.acknowledge == publication.acknowledge
            assert _publication.retain == publication.retain
            assert _publication.exclude_me == publication.exclude_me
            assert _publication.exclude == publication.exclude
            assert _publication.exclude_authid == publication.exclude_authid
            assert _publication.exclude_authrole == publication.exclude_authrole
            assert _publication.eligible == publication.eligible
            assert _publication.eligible_authid == publication.eligible_authid
            assert _publication.eligible_authrole == publication.eligible_authrole
            assert _publication.enc_algo == publication.enc_algo
            assert _publication.enc_key == publication.enc_key
            assert _publication.enc_serializer == publication.enc_serializer

            scratch['timestamp'] += publication.timestamp

    N = 5

    if platform.python_implementation() == 'PyPy':
        M = 100000
    else:
        M = 10000
    samples = []
    print('measuring with N={}, M={}:'.format(N, M))
    for i in range(N):
        secs = timeit.timeit(loop, number=M)
        ops = round(float(M) / secs, 1)
        samples.append(ops)
        print('{} objects/sec performance'.format(ops))

    samples = sorted(samples)
    ops50 = samples[int(len(samples) / 2)]
    print('RESULT: {} objects/sec median performance ({} objects total)'.format(ops50, N * M))

    assert ops50 > 1000
    assert scratch['timestamp'] > 0
