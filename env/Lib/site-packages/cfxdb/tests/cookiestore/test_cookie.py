##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################

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

from cfxdb.cookiestore import Cookie


def fill_cookie(cookie):
    cookie.oid = uuid.uuid4()
    cookie.created = np.datetime64(time_ns(), 'ns')
    cookie.max_age = random.randint(1, 10**10)
    cookie.name = random.choice(['cbtid1', 'cbtid2', 'cbtid3'])
    cookie.value = util.newid(24)
    cookie.authenticated = np.datetime64(time_ns(), 'ns')
    cookie.authenticated_on_node = uuid.uuid4()
    cookie.authenticated_on_worker = random.choice(['worker1', 'worker2', 'worker3'])
    cookie.authenticated_transport_info = {'xoo': 'yar', 'zaz': [9, 8, 7]}
    cookie.authenticated_session = util.id()
    cookie.authenticated_joined_at = np.datetime64(time_ns(), 'ns')
    cookie.authenticated_authmethod = random.choice(['meth1', 'meth2', 'meth3'])
    cookie.authid = util.generate_token(4, 3)
    cookie.authrole = random.choice(['role1', 'role2', 'role3'])
    cookie.authmethod = random.choice(['method1', 'method2', 'method3'])
    cookie.authrealm = random.choice(['realm1', 'realm2', 'realm3'])
    cookie.authextra = {'foo': 'bar', 'baz': [1, 2, 3]}


def fill_cookie_empty(cookie):
    cookie.oid = None
    cookie.created = None
    cookie.max_age = None
    cookie.name = None
    cookie.value = None
    cookie.authenticated = None
    cookie.authenticated_on_node = None
    cookie.authenticated_on_worker = None
    cookie.authenticated_transport_info = None
    cookie.authenticated_session = None
    cookie.authenticated_joined_at = None
    cookie.authenticated_authmethod = None
    cookie.authid = None
    cookie.authrole = None
    cookie.authmethod = None
    cookie.authrealm = None
    cookie.authextra = None


@pytest.fixture(scope='function')
def cookie():
    _cookie = Cookie()
    fill_cookie(_cookie)
    return _cookie


@pytest.fixture(scope='function')
def builder():
    _builder = flatbuffers.Builder(0)
    return _builder


def test_cookie_roundtrip(cookie, builder):
    # serialize to bytes (flatbuffers) from python object
    obj = cookie.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    assert len(data) == 360

    # create python object from bytes (flatbuffes)
    _cookie = Cookie.cast(data)

    assert _cookie.oid == cookie.oid
    assert _cookie.created == cookie.created
    assert _cookie.max_age == cookie.max_age
    assert _cookie.name == cookie.name
    assert _cookie.value == cookie.value
    assert _cookie.authenticated == cookie.authenticated
    assert _cookie.authenticated_on_node == cookie.authenticated_on_node
    assert _cookie.authenticated_on_worker == cookie.authenticated_on_worker
    assert _cookie.authenticated_transport_info == cookie.authenticated_transport_info
    assert _cookie.authenticated_session == cookie.authenticated_session
    assert _cookie.authenticated_joined_at == cookie.authenticated_joined_at
    assert _cookie.authenticated_authmethod == cookie.authenticated_authmethod
    assert _cookie.authid == cookie.authid
    assert _cookie.authrole == cookie.authrole
    assert _cookie.authmethod == cookie.authmethod
    assert _cookie.authrealm == cookie.authrealm
    assert _cookie.authextra == cookie.authextra


def test_cookie_empty(builder):
    cookie = Cookie()
    fill_cookie_empty(cookie)

    # serialize to bytes (flatbuffers) from python object
    obj = cookie.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    assert len(data) == 12

    # create python object from bytes (flatbuffes)
    _cookie = Cookie.cast(data)

    unix_zero = np.datetime64(0, 'ns')

    assert _cookie.oid is None
    assert _cookie.created == unix_zero
    assert _cookie.max_age == 0
    assert _cookie.name is None
    assert _cookie.value is None
    assert _cookie.authenticated == unix_zero
    assert _cookie.authenticated_on_node is None
    assert _cookie.authenticated_on_worker is None
    assert _cookie.authenticated_transport_info == {}
    assert _cookie.authenticated_session == 0
    assert _cookie.authenticated_joined_at == unix_zero
    assert _cookie.authenticated_authmethod is None
    assert _cookie.authid is None
    assert _cookie.authrole is None
    assert _cookie.authmethod is None
    assert _cookie.authrealm is None
    assert _cookie.authextra == {}


def test_cookie_roundtrip_perf(cookie, builder):
    obj = cookie.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    scratch = {'value': 0}

    def loop():
        _cookie = Cookie.cast(data)

        assert _cookie.oid == cookie.oid
        assert _cookie.created == cookie.created
        assert _cookie.max_age == cookie.max_age
        assert _cookie.name == cookie.name
        assert _cookie.value == cookie.value
        assert _cookie.authenticated == cookie.authenticated
        assert _cookie.authenticated_on_node == cookie.authenticated_on_node
        assert _cookie.authenticated_on_worker == cookie.authenticated_on_worker
        assert _cookie.authenticated_transport_info == cookie.authenticated_transport_info
        assert _cookie.authenticated_session == cookie.authenticated_session
        assert _cookie.authenticated_joined_at == cookie.authenticated_joined_at
        assert _cookie.authenticated_authmethod == cookie.authenticated_authmethod
        assert _cookie.authid == cookie.authid
        assert _cookie.authrole == cookie.authrole
        assert _cookie.authmethod == cookie.authmethod
        assert _cookie.authrealm == cookie.authrealm
        assert _cookie.authextra == cookie.authextra

        scratch['value'] += _cookie.authenticated_session

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
