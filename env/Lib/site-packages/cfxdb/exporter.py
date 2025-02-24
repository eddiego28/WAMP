##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################

import os
import sys
import uuid
import json
from pprint import pprint
from typing import List, Dict, Any

from pygments import highlight, lexers, formatters

import cbor2
import click
import numpy as np

import zlmdb
import cfxdb

from autobahn.wamp.serializer import JsonObjectSerializer

from cfxdb.xbrnetwork import Account, UserKey

from txaio import time_ns


def pprint_json(data):
    json_str = json.dumps(data, separators=(', ', ': '), sort_keys=True, indent=4, ensure_ascii=False)
    console_str = highlight(json_str, lexers.JsonLexer(), formatters.Terminal256Formatter(style='fruity'))
    print(console_str)


class Exporter(object):
    """
    CFXDB database exporter.
    """
    def __init__(self, dbpath):
        """

        :param dbpath: Database file to open.
        """
        self._dbpath = os.path.abspath(dbpath)
        self._db = zlmdb.Database(dbpath=self._dbpath, maxsize=2**30, readonly=False)
        self._db.__enter__()

        self._schemata: Dict[str, Any] = {}
        self._schema_tables = {}

        if False:
            self._meta = cfxdb.meta.Schema.attach(self._db)
            self._globalschema = cfxdb.globalschema.GlobalSchema.attach(self._db)
            self._mrealmschema = cfxdb.mrealmschema.MrealmSchema.attach(self._db)
            self._xbr = cfxdb.xbr.Schema.attach(self._db)
            self._xbrmm = cfxdb.xbrmm.Schema.attach(self._db)
            self._xbrnetwork = cfxdb.xbrnetwork.Schema.attach(self._db)

            self._schemata = {
                'meta': self._meta,
                'globalschema': self._globalschema,
                'mrealmschema': self._mrealmschema,
                'xbr': self._xbr,
                'xbrmm': self._xbrmm,
                'xbrnetwork': self._xbrnetwork,
            }
            self._schema_tables = {}
            for schema_name, schema in self._schemata.items():
                tables = {}
                first = None
                for k, v in schema.__annotations__.items():
                    for line in v.__doc__.splitlines():
                        line = line.strip()
                        if line != "":
                            first = line[:80]
                            break
                    tables[k] = first
                self._schema_tables[schema_name] = tables

    @property
    def dbpath(self) -> str:
        """

        :return:
        """
        return self._dbpath

    def schemata(self) -> List[str]:
        """

        :return:
        """
        return sorted(self._schemata.keys())

    def tables(self, schema_name):
        """

        :param schema_name:
        :return:
        """
        if schema_name in self._schema_tables:
            return sorted(self._schema_tables[schema_name].keys())
        else:
            return None

    def table_docs(self, schema_name, table_name):
        """

        :param schema_name:
        :param table_name:
        :return:
        """
        if schema_name in self._schema_tables and table_name in self._schema_tables[schema_name]:
            return self._schema_tables[schema_name][table_name]
        else:
            return None

    def _add_test_data(self):
        account = Account()
        account.oid = uuid.uuid4()
        account.created = np.datetime64(time_ns(), 'ns')
        account.username = 'alice'
        account.email = 'alice@example.com'
        account.wallet_type = 2  # metamask
        account.wallet_address = os.urandom(20)
        # account.wallet_address = binascii.a2b_hex('f5173a6111B2A6B3C20fceD53B2A8405EC142bF6')

        userkey = UserKey()
        userkey.pubkey = os.urandom(32)
        # userkey.pubkey = binascii.a2b_hex('b7e6462121b9632b2bfcc5a3beef0b49dd865093ad003d011d4abbb68476d5b4')
        userkey.created = account.created
        userkey.owner = account.oid

        with self._db.begin(write=True) as txn:
            self._xbrnetwork.accounts[txn, account.oid] = account
            self._xbrnetwork.user_keys[txn, userkey.pubkey] = userkey

    def print_slots(self, include_description=False):
        """

        :param include_description:
        :return:
        """
        print(click.style('Database slots:\n', fg='white', bold=True))
        slots = self._db._get_slots()
        for slot_id in slots:
            slot = slots[slot_id]

            with self._db.begin() as txn:
                pmap = zlmdb.PersistentMap(slot.slot)
                records = pmap.count(txn)

            if include_description:
                print('   Table in slot {} ({}) with {} records is bound to class {}: {}'.format(
                    click.style(str(slot.slot), fg='yellow', bold=True),
                    click.style(str(slot_id), fg='white'), click.style(str(records), fg='yellow', bold=True),
                    click.style(slot.name, fg='yellow'), slot.description))
            else:
                print('   Table in slot {} ({}) with {} records is bound to class {}'.format(
                    click.style(str(slot.slot), fg='yellow', bold=True), click.style(str(slot_id),
                                                                                     fg='white'),
                    click.style(str(records), fg='yellow', bold=True), click.style(slot.name, fg='yellow')))
        print('')

    def print_stats(self, include_slots=False):
        """

        :return:
        """
        print(click.style('Database statistics:\n', fg='white', bold=True))
        pprint_json(self._db.stats(include_slots=include_slots))
        print('')

    def print_config(self):
        print(click.style('Database configuration:\n', fg='white', bold=True))
        pprint_json(self._db.config())
        print('')

    def export_database(self,
                        filename=None,
                        include_indexes=False,
                        include_schemata=None,
                        exclude_tables=None,
                        use_json=False,
                        quiet=False,
                        use_binary_hex_encoding=False):
        """

        :param filename:
        :param include_indexes:
        :param include_schemata:
        :param exclude_tables:
        :param use_json:
        :param use_binary_hex_encoding:
        :returns:
        """
        if include_schemata is None:
            schemata = sorted(self._schemata.keys())
        else:
            assert type(include_schemata) == list
            schemata = sorted(list(set(include_schemata).intersection(self._schemata.keys())))

        if exclude_tables is None:
            exclude_tables = set()
        else:
            assert type(exclude_tables) == list
            exclude_tables = set(exclude_tables)

        result = {}
        with self._db.begin() as txn:
            for schema_name in schemata:
                for table_name in self._schema_tables[schema_name]:
                    fq_table_name = '{}.{}'.format(schema_name, table_name)
                    if fq_table_name not in exclude_tables:
                        table = self._schemata[schema_name].__dict__[table_name]
                        if not table.is_index() or include_indexes:
                            recs = []
                            for key, val in table.select(txn, return_keys=True, return_values=True):
                                if val:
                                    if hasattr(val, 'marshal'):
                                        val = val.marshal()
                                recs.append((table._serialize_key(key), val))
                            if recs:
                                if schema_name not in result:
                                    result[schema_name] = {}
                                result[schema_name][table_name] = recs

        if use_json:
            ser = JsonObjectSerializer(batched=False, use_binary_hex_encoding=use_binary_hex_encoding)
            try:
                data: bytes = ser.serialize(result)
            except TypeError as e:
                print(e)
                pprint(result)
                sys.exit(1)
        else:
            data: bytes = cbor2.dumps(result)

        if filename:
            with open(filename, 'wb') as f:
                f.write(data)
        else:
            sys.stdout.buffer.write(data)

        if not quiet:
            print('\nExported database [dbpath="{dbpath}", filename="{filename}", filesize={filesize}]:\n'.
                  format(dbpath=click.style(self._dbpath, fg='yellow'),
                         filename=click.style(filename, fg='yellow'),
                         filesize=click.style(len(data), fg='yellow')))
            for schema_name in result:
                for table_name in result[schema_name]:
                    cnt = len(result[schema_name][table_name])
                    if cnt:
                        print('{:.<52}: {}'.format(
                            click.style('{}.{}'.format(schema_name, table_name), fg='white', bold=True),
                            click.style(str(cnt) + ' records', fg='yellow')))

    def import_database(self,
                        filename=None,
                        include_indexes=False,
                        include_schemata=None,
                        exclude_tables=None,
                        use_json=False,
                        quiet=False,
                        use_binary_hex_encoding=False):
        """

        :param filename:
        :param include_indexes:
        :param include_schemata:
        :param exclude_tables:
        :param use_json:
        :param use_binary_hex_encoding:
        :returns:
        """
        if include_schemata is None:
            schemata = sorted(self._schemata.keys())
        else:
            assert type(include_schemata) == list
            schemata = sorted(list(set(include_schemata).intersection(self._schemata.keys())))

        if exclude_tables is None:
            exclude_tables = set()
        else:
            assert type(exclude_tables) == list
            exclude_tables = set(exclude_tables)

        if filename:
            with open(filename, 'rb') as f:
                data = f.read()
        else:
            data = sys.stdin.read()

        if use_json:
            ser = JsonObjectSerializer(batched=False, use_binary_hex_encoding=use_binary_hex_encoding)
            db_data = ser.unserialize(data)[0]
        else:
            db_data = cbor2.loads(data)

        if not quiet:
            print('\nImporting database [dbpath="{dbpath}", filename="{filename}", filesize={filesize}]:\n'.
                  format(dbpath=self._dbpath, filename=filename, filesize=len(data)))

        with self._db.begin(write=True) as txn:
            for schema_name in schemata:
                for table_name in self._schema_tables[schema_name]:
                    fq_table_name = '{}.{}'.format(schema_name, table_name)
                    if fq_table_name not in exclude_tables:
                        table = self._schemata[schema_name].__dict__[table_name]
                        if not table.is_index() or include_indexes:
                            if schema_name in db_data and table_name in db_data[schema_name]:
                                cnt = 0
                                for key, val in db_data[schema_name][table_name]:
                                    key = table._deserialize_key(key)
                                    val = table.parse(val)
                                    table[txn, key] = val
                                    cnt += 1
                                if cnt and not quiet:
                                    print('{:.<52}: {}'.format(
                                        click.style('{}.{}'.format(schema_name, table_name),
                                                    fg='white',
                                                    bold=True), click.style(str(cnt) + ' records',
                                                                            fg='yellow')))
                            else:
                                if not quiet:
                                    print('No data to import for {}.{}!'.format(schema_name, table_name))
