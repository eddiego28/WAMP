##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################

import os
import random
import uuid
import shutil
import tempfile
from txaio import time_ns

import numpy as np
import pytest

import txaio
txaio.use_twisted()

import zlmdb

from cfxdb.globalschema import GlobalSchema
from cfxdb.usage import MasterNodeUsage


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


@pytest.fixture(scope='module')
def db(scratch=True):
    dbpath = os.path.join(tempfile.gettempdir(), 'testdb')
    if scratch and os.path.exists(dbpath):
        shutil.rmtree(dbpath)
    db = zlmdb.Database(dbpath=dbpath, writemap=True)
    db.__enter__()
    return db


def test_stats(db):
    dbs = GlobalSchema.attach(db)

    # {'branch_pages': 0,
    # 'current_size': 10485760,
    # 'depth': 1,
    # 'entries': 14,
    # 'free': 0.999609375,
    # 'last_pgno': 7,
    # 'last_txnid': 14,
    # 'leaf_pages': 1,
    # 'map_addr': 0,
    # 'map_size': 10485760,
    # 'max_readers': 126,
    # 'max_size': 10485760,
    # 'num_readers': 1,
    # 'overflow_pages': 0,
    # 'pages': 1,
    # 'pages_size': 4096,
    # 'psize': 4096,
    # 'read_only': False,
    # 'sync_enabled': True,
    # 'zlmdb_slots': 14}
    stats = db.stats()

    # check default maximum size
    assert stats['max_size'] == 10485760

    # check current size, which is maxsize when writemap==True (which it is by default)
    assert stats['current_size'] == 10485760

    # however, the DB is empty ..
    assert stats['pages'] == 1
    assert stats['free'] == 0.999609375

    # GlobalSchema has 14 tables
    assert stats['num_slots'] == 14


def test_usage_stats(db):
    dbs: GlobalSchema = GlobalSchema.attach(db)

    stats_begin = db.stats()
    assert stats_begin['pages'] == 1
    assert stats_begin['free'] == 0.999609375

    with db.begin(write=True) as txn:
        for i in range(10000):
            usage = MasterNodeUsage()
            fill_usage(usage)
            dbs.usage[txn, (usage.timestamp, usage.mrealm_id)] = usage

    stats_end = db.stats()
    assert stats_end['pages'] == 1684
    assert stats_end['free'] == 0.3421875
