##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################

import pytest
import random
import uuid
import timeit

import flatbuffers
import numpy as np

from txaio import with_twisted, time_ns  # noqa

from autobahn import util
from autobahn.wamp.types import TransportDetails
from cfxdb.realmstore import Session

DATA1 = {
    'authextra': {
        'transport': {
            'channel_framing':
            'websocket',
            'channel_id': {},
            'channel_serializer':
            None,
            'channel_type':
            'tcp',
            'http_cbtid':
            'ch0oFqC4EQMCqpYmj/78bQ5D',
            'http_headers_received': {
                'cache-control': 'no-cache',
                'connection': 'Upgrade',
                'host': 'localhost:8080',
                'pragma': 'no-cache',
                'sec-websocket-extensions': 'permessage-deflate; '
                'client_no_context_takeover; '
                'client_max_window_bits',
                'sec-websocket-key': 'FG9K1Vx44MqEE9c37YgPEw==',
                'sec-websocket-protocol': 'wamp.2.json',
                'sec-websocket-version': '13',
                'upgrade': 'WebSocket',
                'user-agent': 'AutobahnPython/22.4.1.dev7'
            },
            'http_headers_sent': {
                'Set-Cookie': 'cbtid=ch0oFqC4EQMCqpYmj/78bQ5D;max-age=604800'
            },
            'is_secure':
            False,
            'is_server':
            True,
            'own':
            None,
            'own_fd':
            -1,
            'own_pid':
            28806,
            'own_tid':
            28806,
            'peer':
            'tcp4:127.0.0.1:48812',
            'peer_cert':
            None,
            'websocket_extensions_in_use': [{
                'client_max_window_bits': 13,
                'client_no_context_takeover': False,
                'extension': 'permessage-deflate',
                'is_server': True,
                'mem_level': 5,
                'server_max_window_bits': 13,
                'server_no_context_takeover': False
            }],
            'websocket_protocol':
            'wamp.2.json'
        },
        'x_cb_node': 'intel-nuci7-28788',
        'x_cb_peer': 'unix',
        'x_cb_pid': 28797,
        'x_cb_worker': 'test_router1'
    },
    'authid': 'client1',
    'authmethod': 'anonymous-proxy',
    'authprovider': 'static',
    'authrole': 'frontend',
    'session': 941369063710961,
    'transport': {
        'channel_framing': 'rawsocket',
        'channel_id': {},
        'channel_serializer': 'cbor',
        'channel_type': 'tcp',
        'http_cbtid': None,
        'http_headers_received': None,
        'http_headers_sent': None,
        'is_secure': False,
        'is_server': None,
        'own': None,
        'own_fd': -1,
        'own_pid': 28797,
        'own_tid': 28797,
        'peer': 'unix',
        'peer_cert': None,
        'websocket_extensions_in_use': None,
        'websocket_protocol': 'wamp.2.cbor'
    }
}

DATA2 = {
    'channel_framing': 'rawsocket',
    'channel_id': {},
    'channel_serializer': 'cbor',
    'channel_type': 'tcp',
    'http_cbtid': None,
    'http_headers_received': None,
    'http_headers_sent': None,
    'is_secure': False,
    'is_server': None,
    'own': None,
    'own_fd': -1,
    'own_pid': 14017,
    'own_tid': 14017,
    'peer': 'unix',
    'peer_cert': None,
    'websocket_extensions_in_use': None,
    'websocket_protocol': 'wamp.2.cbor'
}


def fill_session(session):
    _td1 = TransportDetails.parse(DATA1['transport'])
    _td2 = TransportDetails.parse(DATA1['authextra']['transport'])
    _td3 = TransportDetails.parse(DATA2)

    session.arealm_oid = uuid.uuid4()
    session.oid = uuid.uuid4()
    session.session = util.id()
    session.joined_at = np.datetime64(time_ns() - 723 * 10**9, 'ns')
    session.left_at = np.datetime64(time_ns(), 'ns')
    session.node_oid = uuid.uuid4()
    session.node_authid = 'intel-nuci7'
    session.worker_name = 'router1'
    session.worker_pid = 28797
    session.transport = _td1.marshal()
    session.proxy_node_oid = uuid.uuid4()
    session.proxy_node_authid = 'intel-nuci7'
    session.proxy_worker_name = 'proxy1'
    session.proxy_worker_pid = 30992
    session.proxy_transport = _td3.marshal()
    session.realm = 'realm-{}'.format(uuid.uuid4())
    session.authid = util.generate_serial_number()
    session.authrole = random.choice(['admin', 'user*', 'guest', 'anon*'])
    session.authmethod = random.choice(['wampcra', 'cookie', 'anonymous-proxy'])
    session.authprovider = random.choice(['static', 'dynamic'])
    session.authextra = {
        'transport': _td2.marshal(),
        'x_cb_node': DATA1['authextra'].get('x_cb_node', None),
        'x_cb_peer': DATA1['authextra'].get('x_cb_peer', None),
        'x_cb_pid': DATA1['authextra'].get('x_cb_pid', None),
        'x_cb_worker': DATA1['authextra'].get('x_cb_worker', None),
    }


@pytest.fixture(scope='function')
def builder():
    _builder = flatbuffers.Builder(0)
    return _builder


@pytest.fixture(scope='function')
def session():
    _session = Session()
    fill_session(_session)
    return _session


def test_session_roundtrip(session, builder):
    # serialize to bytes (flatbuffers) from python object
    obj = session.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    assert len(data) in [1944, 1952]

    # create python object from bytes (flatbuffers)
    _session = Session.cast(data)

    assert _session.arealm_oid == session.arealm_oid
    assert _session.oid == session.oid
    assert _session.session == session.session
    assert _session.joined_at == session.joined_at
    assert _session.left_at == session.left_at
    assert _session.node_oid == session.node_oid
    assert _session.node_authid == session.node_authid
    assert _session.worker_name == session.worker_name
    assert _session.worker_pid == session.worker_pid
    assert _session.transport == session.transport
    assert _session.proxy_node_oid == session.proxy_node_oid
    assert _session.proxy_node_authid == session.proxy_node_authid
    assert _session.proxy_worker_name == session.proxy_worker_name
    assert _session.proxy_worker_pid == session.proxy_worker_pid
    assert _session.proxy_transport == session.proxy_transport
    assert _session.realm == session.realm
    assert _session.authid == session.authid
    assert _session.authrole == session.authrole
    assert _session.authmethod == session.authmethod
    assert _session.authprovider == session.authprovider
    assert _session.authextra == session.authextra


def test_session_roundtrip_perf(session, builder):
    obj = session.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    scratch = {'session': 0}

    def loop():
        _session = Session.cast(data)
        if True:
            assert _session.arealm_oid == session.arealm_oid
            assert _session.oid == session.oid
            assert _session.session == session.session
            assert _session.joined_at == session.joined_at
            assert _session.left_at == session.left_at
            assert _session.node_oid == session.node_oid
            assert _session.node_authid == session.node_authid
            assert _session.worker_name == session.worker_name
            assert _session.worker_pid == session.worker_pid
            assert _session.transport == session.transport
            assert _session.proxy_node_oid == session.proxy_node_oid
            assert _session.proxy_node_authid == session.proxy_node_authid
            assert _session.proxy_worker_name == session.proxy_worker_name
            assert _session.proxy_worker_pid == session.proxy_worker_pid
            assert _session.proxy_transport == session.proxy_transport
            assert _session.realm == session.realm
            assert _session.authid == session.authid
            assert _session.authrole == session.authrole
            assert _session.authmethod == session.authmethod
            assert _session.authprovider == session.authprovider
            assert _session.authextra == session.authextra

            scratch['session'] += session.session

    N = 5
    M = 100000
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
    assert scratch['session'] > 0
