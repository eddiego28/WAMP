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

from cfxdb.xbrmm import Transaction


def fill_transaction(transaction):
    now = time_ns()
    transaction.tid = uuid.uuid4()
    transaction.created = np.datetime64(now, 'ns')
    transaction.created_payment_channel_seq = random.randint(1, 1000)
    transaction.created_paying_channel_seq = random.randint(1, 1000)
    transaction.offer = uuid.uuid4()
    transaction.amount = random.randint(1, 2**256 - 1)
    transaction.payment_channel = uuid.uuid4()
    transaction.paying_channel = uuid.uuid4()
    transaction.state = random.randint(1, 3)
    transaction.completed = np.datetime64(now, 'ns')
    transaction.completed_payment_channel_seq = random.randint(1, 1000)
    transaction.completed_paying_channel_seq = random.randint(1, 1000)
    transaction.key = uuid.uuid4()
    transaction.buyer_pubkey = os.urandom(32)
    transaction.payment_channel_after = random.randint(1, 2**256 - 1)
    transaction.paying_channel_after = random.randint(1, 2**256 - 1)
    transaction.payment_mm_sig = os.urandom(65)
    transaction.payment_del_sig = os.urandom(65)
    transaction.paying_mm_sig = os.urandom(65)
    transaction.paying_del_sig = os.urandom(65)


def fill_transaction_empty(transaction):
    transaction.tid = None
    transaction.created = None
    transaction.created_payment_channel_seq = None
    transaction.created_paying_channel_seq = None
    transaction.offer = None
    transaction.amount = None
    transaction.payment_channel = None
    transaction.paying_channel = None
    transaction.state = None
    transaction.completed = None
    transaction.completed_payment_channel_seq = None
    transaction.completed_paying_channel_seq = None
    transaction.key = None
    transaction.buyer_pubkey = None
    transaction.payment_channel_after = None
    transaction.paying_channel_after = None
    transaction.payment_mm_sig = None
    transaction.payment_del_sig = None
    transaction.paying_mm_sig = None
    transaction.paying_del_sig = None


@pytest.fixture(scope='function')
def transaction():
    _transaction = Transaction()
    fill_transaction(_transaction)
    return _transaction


@pytest.fixture(scope='function')
def builder():
    _builder = flatbuffers.Builder(0)
    return _builder


def test_transaction_roundtrip(transaction, builder):
    # serialize to bytes (flatbuffers) from python object
    obj = transaction.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    assert len(data) == 720

    # create python object from bytes (flatbuffes)
    _transaction = Transaction.cast(data)

    assert _transaction.tid == transaction.tid
    assert _transaction.created == transaction.created
    assert _transaction.created_payment_channel_seq == transaction.created_payment_channel_seq
    assert _transaction.created_paying_channel_seq == transaction.created_paying_channel_seq
    assert _transaction.offer == transaction.offer
    assert _transaction.amount == transaction.amount
    assert _transaction.payment_channel == transaction.payment_channel
    assert _transaction.paying_channel == transaction.paying_channel
    assert _transaction.state == transaction.state
    assert _transaction.completed == transaction.completed
    assert _transaction.completed_payment_channel_seq == transaction.completed_payment_channel_seq
    assert _transaction.completed_paying_channel_seq == transaction.completed_paying_channel_seq
    assert _transaction.key == transaction.key
    assert _transaction.buyer_pubkey == transaction.buyer_pubkey
    assert _transaction.payment_channel_after == transaction.payment_channel_after
    assert _transaction.paying_channel_after == transaction.paying_channel_after
    assert _transaction.payment_mm_sig == transaction.payment_mm_sig
    assert _transaction.payment_del_sig == transaction.payment_del_sig
    assert _transaction.paying_mm_sig == transaction.paying_mm_sig
    assert _transaction.paying_del_sig == transaction.paying_del_sig


def test_transaction_empty(builder):
    transaction1 = Transaction()
    fill_transaction_empty(transaction1)

    # serialize to bytes (flatbuffers) from python object
    obj = transaction1.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    assert len(data) == 12

    # create python object from bytes (flatbuffes)
    transaction2 = Transaction.cast(data)

    unix_zero = np.datetime64(0, 'ns')

    assert transaction2.tid is None
    assert transaction2.created == unix_zero
    assert transaction2.created_payment_channel_seq == 0
    assert transaction2.created_paying_channel_seq == 0
    assert transaction2.offer is None
    assert transaction2.amount == 0
    assert transaction2.payment_channel is None
    assert transaction2.paying_channel is None
    assert transaction2.state == 0
    assert transaction2.completed == unix_zero
    assert transaction2.completed_payment_channel_seq == 0
    assert transaction2.completed_paying_channel_seq == 0
    assert transaction2.key is None
    assert transaction2.buyer_pubkey is None
    assert transaction2.payment_channel_after == 0
    assert transaction2.paying_channel_after == 0
    assert transaction2.payment_mm_sig is None
    assert transaction2.payment_del_sig is None
    assert transaction2.paying_mm_sig is None
    assert transaction2.paying_del_sig is None


def test_transaction_roundtrip_perf(transaction, builder):
    obj = transaction.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    scratch = {'value': 0}

    def loop():
        _transaction = Transaction.cast(data)
        if True:
            assert _transaction.tid == transaction.tid
            assert _transaction.created == transaction.created
            assert _transaction.created_payment_channel_seq == transaction.created_payment_channel_seq
            assert _transaction.created_paying_channel_seq == transaction.created_paying_channel_seq
            assert _transaction.offer == transaction.offer
            assert _transaction.amount == transaction.amount
            assert _transaction.payment_channel == transaction.payment_channel
            assert _transaction.paying_channel == transaction.paying_channel
            assert _transaction.state == transaction.state
            assert _transaction.completed == transaction.completed
            assert _transaction.completed_payment_channel_seq == transaction.completed_payment_channel_seq
            assert _transaction.completed_paying_channel_seq == transaction.completed_paying_channel_seq
            assert _transaction.key == transaction.key
            assert _transaction.buyer_pubkey == transaction.buyer_pubkey
            assert _transaction.payment_channel_after == transaction.payment_channel_after
            assert _transaction.paying_channel_after == transaction.paying_channel_after
            assert _transaction.payment_mm_sig == transaction.payment_mm_sig
            assert _transaction.payment_del_sig == transaction.payment_del_sig
            assert _transaction.paying_mm_sig == transaction.paying_mm_sig
            assert _transaction.paying_del_sig == transaction.paying_del_sig

            scratch['value'] += _transaction.amount

    N = 7
    M = 20000
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
