##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################

import os
import uuid
import binascii
from datetime import datetime

import pytest
import cbor2
import flatbuffers

import txaio

from cfxdb.user import User, UserFbs

txaio.use_twisted()


@pytest.fixture(scope='function')
def builder():
    _builder = flatbuffers.Builder(0)
    return _builder


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


def test_user_fbs_roundtrip(user_fbs, builder):
    # serialize to bytes (flatbuffers) from python object
    obj = user_fbs.build(builder)
    builder.Finish(obj)
    data = builder.Output()

    # create python object from bytes (flatbuffes)
    _user = UserFbs.cast(data)

    # assert _user == user_fbs

    assert _user.oid == user_fbs.oid
    assert _user.label == user_fbs.label
    assert _user.description == user_fbs.description
    assert _user.tags == user_fbs.tags
    assert _user.email == user_fbs.email
    assert _user.registered == user_fbs.registered
    assert _user.pubkey == user_fbs.pubkey


def test_user_cbor_roundtrip(user_cbor):
    # serialize to bytes (cbor) from python object
    obj = user_cbor.marshal()
    data = cbor2.dumps(obj)

    # create python object from bytes (cbor)
    _obj = cbor2.loads(data)
    _user = User.parse(_obj)

    # assert _user == user_cbor

    assert _user.oid == user_cbor.oid
    assert _user.label == user_cbor.label
    assert _user.description == user_cbor.description
    assert _user.tags == user_cbor.tags
    assert _user.email == user_cbor.email
    assert _user.registered == user_cbor.registered
    assert _user.pubkey == user_cbor.pubkey


def test_user_copy_cbor_to_fbs(user_cbor):
    user_fbs = UserFbs()
    user_fbs.copy(user_cbor)

    # assert user_fbs == user_cbor

    assert user_fbs.oid == user_cbor.oid
    assert user_fbs.label == user_cbor.label
    assert user_fbs.description == user_cbor.description
    assert user_fbs.tags == user_cbor.tags
    assert user_fbs.email == user_cbor.email
    assert user_fbs.registered == user_cbor.registered
    assert user_fbs.pubkey == user_cbor.pubkey


def test_user_copy_fbs_to_cbor(user_fbs):
    user_cbor = User()
    user_cbor.copy(user_fbs)

    # assert user_fbs == user_cbor

    assert user_fbs.oid == user_cbor.oid
    assert user_fbs.label == user_cbor.label
    assert user_fbs.description == user_cbor.description
    assert user_fbs.tags == user_cbor.tags
    assert user_fbs.email == user_cbor.email
    assert user_fbs.registered == user_cbor.registered
    assert user_fbs.pubkey == user_cbor.pubkey
