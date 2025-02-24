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

from cfxdb.xbr import TokenApproval


def fill_token_approval(token_approval):
    token_approval.tx_hash = os.urandom(32)
    token_approval.block_hash = os.urandom(32)
    token_approval.owner_address = os.urandom(20)
    token_approval.spender_address = os.urandom(20)
    token_approval.value = random.randint(1, 2**256 - 1)


@pytest.fixture(scope='function')
def token_approval():
    _token_approval = TokenApproval()
    fill_token_approval(_token_approval)
    return _token_approval


@pytest.fixture(scope='function')
def builder():
    _builder = flatbuffers.Builder(0)
    return _builder


def test_token_approval_roundtrip(token_approval, builder):
    # serialize to bytes (flatbuffers) from python object
    obj = token_approval.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    assert len(data) == 220

    # create python object from bytes (flatbuffes)
    _token_approval = TokenApproval.cast(data)

    assert _token_approval.tx_hash == token_approval.tx_hash
    assert _token_approval.block_hash == token_approval.block_hash
    assert _token_approval.owner_address == token_approval.owner_address
    assert _token_approval.spender_address == token_approval.spender_address
    assert _token_approval.value == token_approval.value


def test_token_approval_roundtrip_perf(token_approval, builder):
    obj = token_approval.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    scratch = {'value': 0}

    def loop():
        _token_approval = TokenApproval.cast(data)
        if True:
            assert _token_approval.tx_hash == token_approval.tx_hash
            assert _token_approval.block_hash == token_approval.block_hash
            assert _token_approval.owner_address == token_approval.owner_address
            assert _token_approval.spender_address == token_approval.spender_address
            assert _token_approval.value == token_approval.value

            scratch['value'] += int(_token_approval.tx_hash[0])
            scratch['value'] += int(_token_approval.tx_hash[7])
            scratch['value'] += int(_token_approval.tx_hash[19])

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
