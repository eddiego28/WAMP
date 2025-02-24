##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################

import os
import uuid
import timeit
import binascii
from datetime import datetime

import pytest

import cbor2
import flatbuffers

import txaio
from autobahn import util

from cfxdb.user import UserFbs, User, ActivationTokenFbs, ActivationToken

txaio.use_twisted()


@pytest.fixture(scope='function')
def builder():
    _builder = flatbuffers.Builder(0)
    return _builder


#
# ACTIVATION TOKEN
#


def fill_token(token):
    token.oid = uuid.uuid4()

    token.atype = 1
    token.status = 1
    token.created = datetime.utcnow()
    token.completed = None
    token.code = util.generate_activation_code()
    token.email = 'homer.simpson@example.com'
    token.pubkey = binascii.b2a_hex(os.urandom(32)).decode()


@pytest.fixture(scope='function')
def token_fbs():
    _token = ActivationTokenFbs()
    fill_token(_token)
    return _token


@pytest.fixture(scope='function')
def token_cbor():
    _token = ActivationToken()
    fill_token(_token)
    return _token


def test_token_fbs_roundtrip_perf(token_fbs, builder):
    # serialize to bytes (flatbuffers) from python object
    obj = token_fbs.build(builder)
    builder.Finish(obj)
    data = builder.Output()

    # create python object from bytes (flatbuffes)
    def loop():
        _token = ActivationTokenFbs.cast(data)
        if True:
            assert _token.oid == token_fbs.oid
            assert len(str(token_fbs.oid)) == 36
            assert _token.atype == token_fbs.atype
            assert _token.status == token_fbs.status
            assert _token.completed == token_fbs.completed
            assert _token.code == token_fbs.code
            assert _token.email == token_fbs.email
            assert _token.pubkey == token_fbs.pubkey
            assert len(token_fbs.pubkey) == 64

    N = 5
    M = 50000
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


def test_token_cbor_roundtrip_perf(token_cbor):
    # serialize to bytes (cbor) from python object
    obj = token_cbor.marshal()
    data = cbor2.dumps(obj)

    # create python object from bytes (cbor)
    def loop():
        _obj = cbor2.loads(data)
        _token = ActivationToken.parse(_obj)
        if True:
            assert _token.oid == token_cbor.oid
            assert _token.atype == token_cbor.atype
            assert _token.status == token_cbor.status
            assert _token.completed == token_cbor.completed
            assert _token.code == token_cbor.code
            assert _token.email == token_cbor.email
            assert _token.pubkey == token_cbor.pubkey

    N = 5
    M = 50000
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


#
# USER
#


def fill_user(user):
    user.oid = uuid.uuid4()

    user.label = 'Homer the 3rd'
    user.description = 'My motto as a user is: never read the f** manual;)'
    user.tags = ['geek', 'pythonista', 'lemon']

    user.email = 'homer.simpson@example.com'
    user.registered = datetime.utcnow()
    user.pubkey = binascii.b2a_hex(os.urandom(32)).decode()


@pytest.fixture(scope='function')
def user_fbs():
    _user = UserFbs()
    fill_user(_user)
    return _user


@pytest.fixture(scope='function')
def user_cbor():
    _user = User()
    fill_user(_user)
    return _user


def test_user_fbs_roundtrip_perf(user_fbs, builder):
    # serialize to bytes (flatbuffers) from python object
    obj = user_fbs.build(builder)
    builder.Finish(obj)
    data = builder.Output()

    # create python object from bytes (flatbuffes)
    def loop():
        _user = UserFbs.cast(data)
        if True:
            assert _user.oid == user_fbs.oid
            assert len(str(_user.oid)) == 36
            assert _user.label == user_fbs.label
            assert _user.description == user_fbs.description
            assert _user.tags == user_fbs.tags

            assert _user.email == user_fbs.email
            assert _user.registered == user_fbs.registered
            assert _user.pubkey == user_fbs.pubkey
            assert len(_user.pubkey) == 64

    N = 5
    M = 50000
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


def test_user_cbor_roundtrip_perf(user_cbor):
    # serialize to bytes (cbor) from python object
    obj = user_cbor.marshal()
    data = cbor2.dumps(obj)

    # create python object from bytes (cbor)
    def loop():
        _obj = cbor2.loads(data)
        _user = User.parse(_obj)
        if True:
            assert _user.oid == user_cbor.oid
            assert _user.label == user_cbor.label
            assert _user.description == user_cbor.description
            assert _user.tags == user_cbor.tags
            assert _user.email == user_cbor.email
            assert _user.registered == user_cbor.registered
            assert _user.pubkey == user_cbor.pubkey

    N = 5
    M = 50000
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
