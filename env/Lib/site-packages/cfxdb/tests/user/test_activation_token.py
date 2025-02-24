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

from autobahn import util
import txaio

from cfxdb.user import ActivationToken, ActivationTokenFbs

txaio.use_twisted()


@pytest.fixture(scope='function')
def builder():
    _builder = flatbuffers.Builder(0)
    return _builder


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


def test_token_fbs_roundtrip(token_fbs, builder):
    # serialize to bytes (flatbuffers) from python object
    obj = token_fbs.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    assert len(data) == 224

    # create python object from bytes (flatbuffes)
    _token = ActivationTokenFbs.cast(data)

    # assert _token == token_fbs

    assert _token.oid == token_fbs.oid
    assert _token.atype == token_fbs.atype
    assert _token.status == token_fbs.status
    assert _token.completed == token_fbs.completed
    assert _token.code == token_fbs.code
    assert _token.email == token_fbs.email
    assert _token.pubkey == token_fbs.pubkey


def test_token_cbor_roundtrip(token_cbor):
    # serialize to bytes (cbor) from python object
    obj = token_cbor.marshal()
    data = cbor2.dumps(obj)
    assert len(data) == 212

    # create python object from bytes (cbor)
    _obj = cbor2.loads(data)
    _token = ActivationToken.parse(_obj)

    # assert _token == token_cbor

    assert _token.oid == token_cbor.oid
    assert _token.atype == token_cbor.atype
    assert _token.status == token_cbor.status
    assert _token.completed == token_cbor.completed
    assert _token.code == token_cbor.code
    assert _token.email == token_cbor.email
    assert _token.pubkey == token_cbor.pubkey


def test_token_copy_cbor_to_fbs(token_cbor):
    token_fbs = ActivationTokenFbs()
    token_fbs.copy(token_cbor)

    # assert token_fbs == token_cbor

    assert token_fbs.oid == token_cbor.oid
    assert token_fbs.atype == token_cbor.atype
    assert token_fbs.status == token_cbor.status
    assert token_fbs.completed == token_cbor.completed
    assert token_fbs.code == token_cbor.code
    assert token_fbs.email == token_cbor.email
    assert token_fbs.pubkey == token_cbor.pubkey


def test_token_copy_fbs_to_cbor(token_fbs):
    token_cbor = ActivationToken()
    token_cbor.copy(token_fbs)

    # assert token_cbor == token_fbs

    assert token_cbor.oid == token_fbs.oid
    assert token_cbor.atype == token_fbs.atype
    assert token_cbor.status == token_fbs.status
    assert token_cbor.completed == token_fbs.completed
    assert token_cbor.code == token_fbs.code
    assert token_cbor.email == token_fbs.email
    assert token_cbor.pubkey == token_fbs.pubkey
