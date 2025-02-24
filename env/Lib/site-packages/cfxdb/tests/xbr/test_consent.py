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

from cfxdb.xbr.consent import Consent
from cfxdb.tests._util import _gen_ipfs_hash

zlmdb.TABLES_BY_UUID = {}


def fill_consent(consent):
    consent.market_oid = uuid.uuid4()
    consent.member = os.urandom(20)
    consent.delegate = os.urandom(20)
    consent.delegate_type = random.randint(1, 3)
    consent.catalog_oid = uuid.uuid4()
    consent.timestamp = np.datetime64(time_ns(), 'ns')
    consent.updated = random.randint(1, 2**256 - 1)
    consent.consent = True
    consent.synced = True
    consent.service_prefix = _gen_ipfs_hash()
    consent.tid = os.urandom(32)
    consent.signature = os.urandom(65)


@pytest.fixture(scope='function')
def builder():
    _builder = flatbuffers.Builder(0)
    return _builder


@pytest.fixture(scope='function')
def consent():
    _consent = Consent()
    fill_consent(_consent)
    return _consent


def test_consent_roundtrip(consent, builder):
    # serialize to bytes (flatbuffers) from python object
    obj = consent.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    assert len(data) == 392

    # create python object from bytes (flatbuffes)
    _consent = Consent.cast(data)

    assert _consent.market_oid == consent.market_oid
    assert _consent.member == consent.member
    assert _consent.delegate == consent.delegate
    assert _consent.delegate_type == consent.delegate_type
    assert _consent.catalog_oid == consent.catalog_oid
    assert _consent.timestamp == consent.timestamp
    assert _consent.updated == consent.updated
    assert _consent.consent == consent.consent
    assert _consent.service_prefix == consent.service_prefix
    assert _consent.tid == consent.tid
    assert _consent.signature == consent.signature
    assert _consent.synced == consent.synced


def test_consent_roundtrip_perf(consent, builder):
    obj = consent.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    scratch = {'value': 0}

    def loop():
        _consent = Consent.cast(data)
        if True:
            assert _consent.market_oid == consent.market_oid
            assert _consent.member == consent.member
            assert _consent.delegate == consent.delegate
            assert _consent.delegate_type == consent.delegate_type
            assert _consent.catalog_oid == consent.catalog_oid
            assert _consent.timestamp == consent.timestamp
            assert _consent.updated == consent.updated
            assert _consent.consent == consent.consent
            assert _consent.service_prefix == consent.service_prefix
            assert _consent.tid == consent.tid
            assert _consent.signature == consent.signature
            assert _consent.synced == consent.synced

            scratch['value'] += _consent.updated

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
