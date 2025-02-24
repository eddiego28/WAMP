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

from cfxdb.xbr import Member
from cfxdb.tests._util import _gen_ipfs_hash


def fill_member(member):
    member.address = os.urandom(20)
    member.account_oid = uuid.uuid4()
    member.timestamp = np.datetime64(time_ns(), 'ns')
    member.registered = random.randint(0, 2**256 - 1)
    member.eula = _gen_ipfs_hash()
    member.profile = _gen_ipfs_hash()
    member.level = random.randint(1, 5)
    member.tid = os.urandom(32)
    member.signature = os.urandom(65)


@pytest.fixture(scope='function')
def member():
    _member = Member()
    fill_member(_member)
    return _member


@pytest.fixture(scope='function')
def builder():
    _builder = flatbuffers.Builder(0)
    return _builder


def test_member_roundtrip(member, builder):
    # serialize to bytes (flatbuffers) from python object
    obj = member.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    assert len(data) == 384

    # create python object from bytes (flatbuffes)
    _member = Member.cast(data)

    assert _member.address == member.address
    assert _member.account_oid == member.account_oid
    assert _member.timestamp == member.timestamp
    assert _member.registered == member.registered
    assert _member.eula == member.eula
    assert _member.profile == member.profile
    assert _member.level == member.level
    assert _member.tid == member.tid
    assert _member.signature == member.signature


def test_member_roundtrip_perf(member, builder):
    obj = member.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    scratch = {'value': 0}

    def loop():
        _member = Member.cast(data)
        if True:
            assert _member.address == member.address
            assert _member.account_oid == member.account_oid
            assert _member.timestamp == member.timestamp
            assert _member.registered == member.registered
            assert _member.eula == member.eula
            assert _member.profile == member.profile
            assert _member.level == member.level
            assert _member.tid == member.tid
            assert _member.signature == member.signature

            scratch['value'] += _member.level

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
