##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################

import os
import random
import pytest
import timeit
import uuid

import numpy as np
import flatbuffers

import zlmdb

import txaio
txaio.use_twisted()  # noqa

from txaio import time_ns

from cfxdb.xbr.api import Api
from cfxdb.tests._util import _gen_ipfs_hash

zlmdb.TABLES_BY_UUID = {}


def fill_api(api):
    api.oid = uuid.uuid4()
    api.catalog_oid = uuid.uuid4()
    api.timestamp = np.datetime64(time_ns(), 'ns')
    api.published = random.randint(0, 2**256 - 1)
    api.schema = _gen_ipfs_hash()
    api.meta = _gen_ipfs_hash()
    api.tid = os.urandom(32)
    api.signature = os.urandom(65)


@pytest.fixture(scope='function')
def builder():
    _builder = flatbuffers.Builder(0)
    return _builder


@pytest.fixture(scope='function')
def api():
    _api = Api()
    fill_api(_api)
    return _api


def test_api_roundtrip(api: Api, builder):
    # serialize to bytes (flatbuffers) from python object
    obj = api.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    assert len(data) == 368

    # create python object from bytes (flatbuffes)
    _api = Api.cast(data)

    assert _api.oid == api.oid
    assert _api.catalog_oid == api.catalog_oid
    assert _api.timestamp == api.timestamp
    assert _api.published == api.published
    assert _api.schema == api.schema
    assert _api.meta == api.meta
    assert _api.tid == api.tid
    assert _api.signature == api.signature


def test_api_roundtrip_perf(api, builder):
    obj = api.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    scratch = {'value': 0}

    def loop():
        _api = Api.cast(data)
        if True:
            assert _api.oid == api.oid
            assert _api.catalog_oid == api.catalog_oid
            assert _api.timestamp == api.timestamp
            assert _api.published == api.published
            assert _api.schema == api.schema
            assert _api.meta == api.meta
            assert _api.tid == api.tid
            assert _api.signature == api.signature

            scratch['value'] += _api.published

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
