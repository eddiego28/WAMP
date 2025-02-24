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

from cfxdb.xbr.catalog import Catalog
from cfxdb.tests._util import _gen_ipfs_hash

zlmdb.TABLES_BY_UUID = {}


def fill_catalog(catalog):
    catalog.oid = uuid.uuid4()
    catalog.timestamp = np.datetime64(time_ns(), 'ns')
    catalog.seq = random.randint(1, 2**32 - 1)
    catalog.owner = os.urandom(20)
    catalog.terms = _gen_ipfs_hash()
    catalog.meta = _gen_ipfs_hash()
    catalog.tid = os.urandom(32)
    catalog.signature = os.urandom(65)


@pytest.fixture(scope='function')
def builder():
    _builder = flatbuffers.Builder(0)
    return _builder


@pytest.fixture(scope='function')
def catalog():
    _catalog = Catalog()
    fill_catalog(_catalog)
    return _catalog


def test_catalog_roundtrip(catalog, builder):
    # serialize to bytes (flatbuffers) from python object
    obj = catalog.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    # assert len(data) == 368

    # create python object from bytes (flatbuffes)
    _catalog = Catalog.cast(data)

    assert _catalog.oid == catalog.oid
    assert _catalog.timestamp == catalog.timestamp
    assert _catalog.seq == catalog.seq
    assert _catalog.owner == catalog.owner
    assert _catalog.terms == catalog.terms
    assert _catalog.meta == catalog.meta
    assert _catalog.tid == catalog.tid
    assert _catalog.signature == catalog.signature


def test_catalog_roundtrip_perf(catalog, builder):
    obj = catalog.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    scratch = {'value': 0}

    def loop():
        _catalog = Catalog.cast(data)
        if True:
            assert _catalog.oid == catalog.oid
            assert _catalog.timestamp == catalog.timestamp
            assert _catalog.seq == catalog.seq
            assert _catalog.terms == catalog.terms
            assert _catalog.meta == catalog.meta
            assert _catalog.tid == catalog.tid
            assert _catalog.signature == catalog.signature

            scratch['value'] += _catalog.seq

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
