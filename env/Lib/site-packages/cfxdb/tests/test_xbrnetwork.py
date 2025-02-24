##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################

import os
import uuid
import random
import timeit
import pytest

import numpy as np
import flatbuffers

import zlmdb

import txaio
txaio.use_twisted()  # noqa

from txaio import time_ns
from autobahn.util import generate_activation_code
from cfxdb.xbrnetwork import Account, VerifiedAction, UserKey

from cfxdb.tests._util import _gen_ipfs_hash

zlmdb.TABLES_BY_UUID = {}


@pytest.fixture(scope='function')
def builder():
    _builder = flatbuffers.Builder(0)
    return _builder


#
# Account
#


def fill_account(account):
    now = time_ns()
    account.oid = uuid.uuid4()
    account.created = np.datetime64(now, 'ns')
    account.username = 'user{}'.format(random.randint(0, 1000))
    account.email = '{}@example.com'.format(account.username)
    account.email_verified = np.datetime64(now + random.randint(10 * 10**9, 60 * 10**9), 'ns')
    account.wallet_type = random.randint(1, 3)
    account.wallet_address = os.urandom(20)
    account.registered = random.randint(0, 2**256 - 1)
    account.eula = _gen_ipfs_hash()
    account.profile = _gen_ipfs_hash()
    account.level = random.randint(1, 5)


@pytest.fixture(scope='function')
def account():
    _account = Account()
    fill_account(_account)
    return _account


def test_account_roundtrip(account, builder):
    # serialize to bytes (flatbuffers) from python object
    obj = account.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    assert len(data) == 328

    # create python object from bytes (flatbuffes)
    _account = Account.cast(data)

    assert _account.oid == account.oid
    assert _account.created == account.created
    assert _account.username == account.username
    assert _account.email == account.email
    assert _account.email_verified == account.email_verified
    assert _account.wallet_type == account.wallet_type
    assert _account.wallet_address == account.wallet_address
    assert _account.registered == account.registered
    assert _account.eula == account.eula
    assert _account.profile == account.profile
    assert _account.level == account.level


def test_account_roundtrip_perf(account, builder):
    obj = account.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    scratch = {'value': 0}

    def loop():
        _account = Account.cast(data)
        if True:
            assert _account.oid == account.oid
            assert _account.created == account.created
            assert _account.username == account.username
            assert _account.email == account.email
            assert _account.email_verified == account.email_verified
            assert _account.wallet_type == account.wallet_type
            assert _account.wallet_address == account.wallet_address
            assert _account.registered == account.registered
            assert _account.eula == account.eula
            assert _account.profile == account.profile
            assert _account.level == account.level

            scratch['value'] += _account.level

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


#
# VerifiedAction
#


def fill_vaction(vaction):
    vaction.oid = uuid.uuid4()
    vaction.created = np.datetime64(time_ns(), 'ns')
    vaction.vtype = random.randint(1, 4)
    vaction.vstatus = random.randint(1, 4)
    vaction.vcode = generate_activation_code()
    vaction.verified_oid = uuid.uuid4()
    vaction.verified_data = {
        'f1': os.urandom(32),
        'f2': random.randint(1, 100),
        'f3': list(range(10)),
        'f4': generate_activation_code()
    }


@pytest.fixture(scope='function')
def vaction():
    _vaction = VerifiedAction()
    fill_vaction(_vaction)
    return _vaction


def test_vaction_roundtrip(vaction, builder):
    # serialize to bytes (flatbuffers) from python object
    obj = vaction.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    assert len(data) == 208

    # create python object from bytes (flatbuffes)
    _vaction = VerifiedAction.cast(data)

    assert _vaction.oid == vaction.oid
    assert _vaction.created == vaction.created
    assert _vaction.vtype == vaction.vtype
    assert _vaction.vstatus == vaction.vstatus
    assert _vaction.vcode == vaction.vcode
    assert _vaction.verified_oid == vaction.verified_oid
    assert _vaction.verified_data == vaction.verified_data


def test_vaction_roundtrip_perf(vaction, builder):
    obj = vaction.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    scratch = {'value': 0}

    def loop():
        _vaction = VerifiedAction.cast(data)
        if True:
            assert _vaction.oid == vaction.oid
            assert _vaction.created == vaction.created
            assert _vaction.vtype == vaction.vtype
            assert _vaction.vstatus == vaction.vstatus
            assert _vaction.vcode == vaction.vcode
            assert _vaction.verified_oid == vaction.verified_oid
            assert _vaction.verified_data == vaction.verified_data

            scratch['value'] += _vaction.vstatus

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


#
# UserKey
#


def fill_userkey(userkey):
    userkey.pubkey = os.urandom(32)
    userkey.created = np.datetime64(time_ns(), 'ns')
    userkey.owner = uuid.uuid4()


@pytest.fixture(scope='function')
def userkey():
    _userkey = UserKey()
    fill_userkey(_userkey)
    return _userkey


def test_userkey_roundtrip(userkey, builder):
    # serialize to bytes (flatbuffers) from python object
    obj = userkey.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    assert len(data) == 104

    # create python object from bytes (flatbuffes)
    _userkey = UserKey.cast(data)

    assert _userkey.pubkey == userkey.pubkey
    assert _userkey.created == userkey.created
    assert _userkey.owner == userkey.owner


def test_userkey_roundtrip_perf(userkey, builder):
    obj = userkey.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    scratch = {'value': 0}

    def loop():
        _userkey = UserKey.cast(data)
        if True:
            assert _userkey.pubkey == userkey.pubkey
            assert _userkey.created == userkey.created
            assert _userkey.owner == userkey.owner

            scratch['value'] += int(_userkey.created)

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
