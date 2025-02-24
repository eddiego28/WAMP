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

from autobahn import util
import flatbuffers
import pytest
import numpy as np
from txaio import time_ns

from cfxdb.xbrmm import Offer


def fill_offer(offer):
    now = time_ns()
    offer.timestamp = np.datetime64(now, 'ns')
    offer.offer = uuid.uuid4()
    offer.seller = os.urandom(20)
    offer.seller_session_id = random.randint(0, 2**53)
    offer.seller_authid = util.generate_token(5, 4)
    offer.key = uuid.uuid4()
    offer.api = uuid.uuid4()
    offer.uri = 'com.example.something.add2'
    offer.valid_from = np.datetime64(now, 'ns')
    offer.signature = os.urandom(64)
    offer.price = random.randint(0, 2**256 - 1)
    offer.categories = {
        'xtile': '{:05}'.format(random.randint(0, 99999)),
        'ytile': '{:05}'.format(random.randint(0, 99999)),
    }
    offer.expires = np.datetime64(now + 60 * 60 * 10**9, 'ns')
    offer.copies = 1000
    offer.remaining = random.randint(0, 1000)


def fill_offer_empty(offer):
    offer.timestamp = None
    offer.offer = None
    offer.seller = None
    offer.seller_session_id = None
    offer.seller_authid = None
    offer.key = None
    offer.api = None
    offer.uri = None
    offer.valid_from = None
    offer.signature = None
    offer.price = None
    offer.categories = None
    offer.expires = None
    offer.copies = None
    offer.remaining = None


@pytest.fixture(scope='function')
def offer():
    _offer = Offer()
    fill_offer(_offer)
    return _offer


@pytest.fixture(scope='function')
def builder():
    _builder = flatbuffers.Builder(0)
    return _builder


def test_offer_roundtrip(offer, builder):
    # serialize to bytes (flatbuffers) from python object
    obj = offer.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    assert len(data) == 480

    # create python object from bytes (flatbuffes)
    _offer = Offer.cast(data)

    assert _offer.timestamp == offer.timestamp
    assert _offer.offer == offer.offer
    assert _offer.seller == offer.seller
    assert _offer.seller_session_id == offer.seller_session_id
    assert _offer.seller_authid == offer.seller_authid
    assert _offer.key == offer.key
    assert _offer.api == offer.api
    assert _offer.uri == offer.uri
    assert _offer.valid_from == offer.valid_from
    assert _offer.signature == offer.signature
    assert _offer.price == offer.price
    assert _offer.categories == offer.categories
    assert _offer.expires == offer.expires
    assert _offer.copies == offer.copies
    assert _offer.remaining == offer.remaining


def test_offer_empty(builder):
    offer = Offer()
    fill_offer_empty(offer)

    # serialize to bytes (flatbuffers) from python object
    obj = offer.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    assert len(data) == 12

    # create python object from bytes (flatbuffes)
    _offer = Offer.cast(data)

    unix_zero = np.datetime64(0, 'ns')

    assert _offer.timestamp == unix_zero
    assert _offer.offer is None
    assert _offer.seller is None
    assert _offer.seller_session_id == 0
    assert _offer.seller_authid is None
    assert _offer.key is None
    assert _offer.api is None
    assert _offer.uri is None
    assert _offer.valid_from == unix_zero
    assert _offer.signature is None
    assert _offer.price == 0
    assert _offer.categories is None
    assert _offer.expires == unix_zero
    assert _offer.copies == 0
    assert _offer.remaining == 0


def test_offer_roundtrip_perf(offer, builder):
    obj = offer.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    scratch = {'value': 0}

    def loop():
        _offer = Offer.cast(data)
        if True:
            assert _offer.timestamp == offer.timestamp
            assert _offer.offer == offer.offer
            assert _offer.seller == offer.seller
            assert _offer.seller_session_id == offer.seller_session_id
            assert _offer.seller_authid == offer.seller_authid
            assert _offer.key == offer.key
            assert _offer.api == offer.api
            assert _offer.uri == offer.uri
            assert _offer.valid_from == offer.valid_from
            assert _offer.signature == offer.signature
            assert _offer.price == offer.price
            assert _offer.categories == offer.categories
            assert _offer.expires == offer.expires
            assert _offer.copies == offer.copies
            assert _offer.remaining == offer.remaining

            scratch['value'] += _offer.price

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
