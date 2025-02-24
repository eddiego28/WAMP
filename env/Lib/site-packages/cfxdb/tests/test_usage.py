##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################

import os
import pytest
import random
import uuid
import timeit

import flatbuffers
import numpy as np

import zlmdb
import txaio
from txaio import time_ns

from cfxdb.usage import MasterNodeUsage

zlmdb.TABLES_BY_UUID = {}
txaio.use_twisted()


@pytest.fixture(scope='function')
def builder():
    _builder = flatbuffers.Builder(0)
    return _builder


#
# Usage
#


def fill_usage(usage):
    usage.timestamp = np.datetime64(time_ns(), 'ns')
    usage.mrealm_id = uuid.uuid4()
    usage.timestamp_from = np.datetime64(usage.timestamp - np.timedelta64(10, 'm'), 'ns')
    usage.pubkey = os.urandom(32)

    usage.client_ip_version = random.choice([4, 6])
    if usage.client_ip_version == 4:
        usage.client_ip_address = os.urandom(4)
    else:
        usage.client_ip_address = os.urandom(16)
    usage.client_ip_port = random.randint(1, 2**16 - 1)

    usage.seq = random.randint(0, 1000000)
    usage.sent = np.datetime64(time_ns() - random.randint(0, 10**10), 'ns')
    usage.processed = np.datetime64(time_ns() + random.randint(0, 10**10), 'ns')
    usage.status = random.randint(0, 3)
    usage.status_message = 'hello world {}'.format(uuid.uuid4())
    usage.metering_id = uuid.uuid4()

    usage.count = random.randint(0, 100000)
    usage.total = random.randint(0, 100000)
    usage.nodes = random.randint(0, 100000)

    usage.controllers = random.randint(0, 100000)
    usage.hostmonitors = random.randint(0, 100000)
    usage.routers = random.randint(0, 100000)
    usage.containers = random.randint(0, 100000)
    usage.guests = random.randint(0, 100000)
    usage.proxies = random.randint(0, 100000)
    usage.marketmakers = random.randint(0, 100000)

    usage.sessions = random.randint(0, 100000)

    usage.msgs_call = random.randint(0, 100000)
    usage.msgs_yield = random.randint(0, 100000)
    usage.msgs_invocation = random.randint(0, 100000)
    usage.msgs_result = random.randint(0, 100000)
    usage.msgs_error = random.randint(0, 100000)
    usage.msgs_publish = random.randint(0, 100000)
    usage.msgs_published = random.randint(0, 100000)
    usage.msgs_event = random.randint(0, 100000)
    usage.msgs_register = random.randint(0, 100000)
    usage.msgs_registered = random.randint(0, 100000)
    usage.msgs_subscribe = random.randint(0, 100000)
    usage.msgs_subscribed = random.randint(0, 100000)


@pytest.fixture(scope='function')
def usage():
    _usage = MasterNodeUsage()
    fill_usage(_usage)
    return _usage


def test_usage_roundtrip(usage, builder):
    # serialize to bytes (flatbuffers) from python object
    obj = usage.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    assert len(data) in [520, 512, 504]

    # create python object from bytes (flatbuffes)
    _usage = MasterNodeUsage.cast(data)

    assert _usage.timestamp == _usage.timestamp
    assert _usage.mrealm_id == _usage.mrealm_id
    assert _usage.timestamp_from == _usage.timestamp_from
    assert _usage.pubkey == _usage.pubkey
    assert _usage.client_ip_address == _usage.client_ip_address
    assert _usage.client_ip_version == _usage.client_ip_version
    assert _usage.client_ip_port == _usage.client_ip_port
    assert _usage.seq == _usage.seq
    assert _usage.sent == _usage.sent
    assert _usage.processed == _usage.processed
    assert _usage.status == _usage.status
    assert _usage.status_message == _usage.status_message
    assert _usage.metering_id == _usage.metering_id

    assert _usage.count == _usage.count
    assert _usage.total == _usage.total
    assert _usage.nodes == _usage.nodes
    assert _usage.controllers == _usage.controllers
    assert _usage.hostmonitors == _usage.hostmonitors
    assert _usage.routers == _usage.routers
    assert _usage.containers == _usage.containers
    assert _usage.guests == _usage.guests
    assert _usage.proxies == _usage.proxies
    assert _usage.marketmakers == _usage.marketmakers
    assert _usage.sessions == _usage.sessions
    assert _usage.msgs_call == _usage.msgs_call
    assert _usage.msgs_yield == _usage.msgs_yield
    assert _usage.msgs_invocation == _usage.msgs_invocation
    assert _usage.msgs_result == _usage.msgs_result
    assert _usage.msgs_error == _usage.msgs_error
    assert _usage.msgs_publish == _usage.msgs_publish
    assert _usage.msgs_published == _usage.msgs_published
    assert _usage.msgs_event == _usage.msgs_event
    assert _usage.msgs_register == _usage.msgs_register
    assert _usage.msgs_registered == _usage.msgs_registered
    assert _usage.msgs_subscribe == _usage.msgs_subscribe
    assert _usage.msgs_subscribed == _usage.msgs_subscribed


def test_usage_roundtrip_perf(usage, builder):
    obj = usage.build(builder)
    builder.Finish(obj)
    data = builder.Output()
    scratch = {}

    def loop():
        _usage = MasterNodeUsage.cast(data)
        if True:

            assert _usage.timestamp == _usage.timestamp
            assert _usage.mrealm_id == _usage.mrealm_id
            assert _usage.timestamp_from == _usage.timestamp_from
            assert _usage.pubkey == _usage.pubkey
            assert _usage.client_ip_address == _usage.client_ip_address
            assert _usage.client_ip_version == _usage.client_ip_version
            assert _usage.client_ip_port == _usage.client_ip_port
            assert _usage.seq == _usage.seq
            assert _usage.sent == _usage.sent
            assert _usage.processed == _usage.processed
            assert _usage.status == _usage.status
            assert _usage.status_message == _usage.status_message
            assert _usage.metering_id == _usage.metering_id

            assert _usage.count == _usage.count
            assert _usage.total == _usage.total
            assert _usage.nodes == _usage.nodes
            assert _usage.controllers == _usage.controllers
            assert _usage.hostmonitors == _usage.hostmonitors
            assert _usage.routers == _usage.routers
            assert _usage.containers == _usage.containers
            assert _usage.guests == _usage.guests
            assert _usage.proxies == _usage.proxies
            assert _usage.marketmakers == _usage.marketmakers
            assert _usage.sessions == _usage.sessions
            assert _usage.msgs_call == _usage.msgs_call
            assert _usage.msgs_yield == _usage.msgs_yield
            assert _usage.msgs_invocation == _usage.msgs_invocation
            assert _usage.msgs_result == _usage.msgs_result
            assert _usage.msgs_error == _usage.msgs_error
            assert _usage.msgs_publish == _usage.msgs_publish
            assert _usage.msgs_published == _usage.msgs_published
            assert _usage.msgs_event == _usage.msgs_event
            assert _usage.msgs_register == _usage.msgs_register
            assert _usage.msgs_registered == _usage.msgs_registered
            assert _usage.msgs_subscribe == _usage.msgs_subscribe
            assert _usage.msgs_subscribed == _usage.msgs_subscribed

            # copy, because of "cannot hash writable memoryview object"
            pubkey = bytes(_usage.pubkey)

            if pubkey not in scratch:
                scratch[pubkey] = 0
            scratch[pubkey] += 1

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
    assert len(scratch) > 0
