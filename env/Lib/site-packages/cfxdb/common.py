##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################

import web3
import struct
import uuid
import pprint


def unpack_uint256(data):
    assert data is None or type(data) == bytes, 'data must by bytes, was {}'.format(type(data))
    if data and type(data) == bytes:
        assert len(data) == 32, 'data must be bytes[32], but was bytes[{}]'.format(len(data))

    if data:
        return web3.Web3.toInt(data)
    else:
        return 0


def pack_uint256(value):
    assert value is None or (type(value) == int and value >= 0
                             and value < 2**256), 'value must be uint256, but was {}'.format(value)

    if value:
        data = web3.Web3.toBytes(value)
        return b'\x00' * (32 - len(data)) + data
    else:
        return b'\x00' * 32


class uint256(object):
    def __init__(self, data=None):
        self._data = data or b'\x00' * 32

    @property
    def value(self):
        return unpack_uint256(self._data)

    @value.setter
    def value(self, value):
        self._data = pack_uint256(value)

    def serialize(self):
        return self._data


def unpack_uint128(data):
    assert data is None or (type(data) == bytes and len(data) == 16)

    if data:
        return web3.Web3.toInt(data)
    else:
        return 0


def pack_uint128(value):
    assert value is None or (type(value) == int and value >= 0 and value < 2**128)

    if value:
        data = web3.Web3.toBytes(value)
        return b'\x00' * (16 - len(data)) + data
    else:
        return b'\x00' * 16


class uint128(object):
    def __init__(self, data=None):
        self._data = data or b'\x00' * 16

    @property
    def value(self):
        return unpack_uint128(self._data)

    @value.setter
    def value(self, value):
        self._data = pack_uint128(value)

    def serialize(self):
        return self._data


def unpack_uint64(data):
    assert data is None or (type(data) == bytes and len(data) == 8)

    if data:
        return web3.Web3.toInt(data)
    else:
        return 0


def pack_uint64(value):
    assert value is None or (type(value) == int and value >= 0 and value < 2**64)

    if value:
        data = web3.Web3.toBytes(value)
        return b'\x00' * (8 - len(data)) + data
    else:
        return b'\x00' * 8


class uint64(object):
    def __init__(self, data=None):
        self._data = data or b'\x00' * 8

    @property
    def value(self):
        return unpack_uint64(self._data)

    @value.setter
    def value(self, value):
        self._data = pack_uint64(value)

    def serialize(self):
        return self._data


class address(object):
    def __init__(self, data=None):
        self._data = data or b'\x00' * 20

    @property
    def value(self):
        w2, w1, w0 = struct.unpack('>LQQ', self._data)
        return w2 << 16 + w1 << 8 + w0

    @value.setter
    def value(self, value):
        assert (type(value) == int and value >= 0 and value < 2**160)
        w0 = value % 2**64
        value = value >> 8
        w1 = value % 2**64
        value = value >> 8
        w2 = value % 2**32
        self._data = struct.pack('>LQQ', w2, w1, w0)

    def serialize(self):
        return self._data


class ConfigurationElement(object):
    """
    CFC configuration element, an abstract "thing" with a unique identifier ("oid",
    which is of type UUID) and that can be user documented using

    * label
    * description
    * tags

    These elements are under user (application) control and not interpreted by
    the CFC backend code (beyond their basic types of string or list of string).

    Configuration elements can be nearly everything in CFC configuration:

    * Users
    * Mrealms
    * Nodes
    * ...
    """

    # oid: uuid.UUID
    oid = None
    """
    Object ID.
    """

    # label: Optional[str]
    label = None
    """
    User label for object (optional free text).
    """

    # description: Optional[str]
    description = None
    """
    User description for object (optional free text)
    """

    # tags: Optional[List[str]]
    tags = None
    """
    User tags for object (optional free list of text portions)
    """
    def __init__(self, oid=None, label=None, description=None, tags=None, _unknown=None):
        self.oid = oid

        self.label = label
        self.description = description
        self.tags = tags

        # private member with unknown/untouched data passing through
        self._unknown = _unknown

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if other.oid != self.oid:
            return False
        if other.label != self.label:
            return False
        if other.description != self.description:
            return False
        if (self.tags and not other.tags) or (not self.tags and other.tags):
            return False
        if other.tags and self.tags:
            if set(other.tags) ^ set(self.tags):
                return False

        # _unknown is not part of comparison

        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return pprint.pformat(self.marshal())

    def copy(self, other, overwrite=False):
        if (not self.oid and other.oid) or overwrite:
            self.oid = other.oid
        if (not self.label and other.label) or overwrite:
            self.label = other.label
        if (not self.description and other.description) or overwrite:
            self.description = other.description
        if (not self.tags and other.tags) or overwrite:
            self.tags = other.tags

        # _unknown is not copied

    def marshal(self):
        assert self.oid is None or isinstance(self.oid, uuid.UUID)
        assert self.label is None or type(self.label) == str
        assert self.description is None or type(self.description) == str
        assert self.tags is None or (type(self.tags) == list and type(tag) == str for tag in self.tags)

        obj = dict()
        obj['oid'] = str(self.oid) if self.oid else None
        obj['label'] = self.label
        obj['description'] = self.description
        obj['tags'] = self.tags

        return obj

    @staticmethod
    def parse(data):
        assert type(data) == dict

        # future attributes (yet unknown) are not only ignored, but passed through!
        _unknown = dict()
        for k in data:
            if k not in ['oid', 'label', 'description', 'tags']:
                _unknown[k] = data[k]

        oid = None
        if 'oid' in data and data['oid'] is not None:
            assert type(data['oid']) == str
            oid = uuid.UUID(data['oid'])

        label = None
        if 'label' in data and data['label'] is not None:
            assert type(data['label']) == str
            label = data['label']

        description = None
        if 'description' in data and data['description'] is not None:
            assert type(data['description']) == str
            description = data['description']

        tags = None
        if 'tags' in data and data['tags'] is not None:
            assert type(data['tags']) == list
            for tag in data['tags']:
                assert type(tag) == str
            tags = data['tags']

        obj = ConfigurationElement(oid=oid,
                                   label=label,
                                   description=description,
                                   tags=tags,
                                   _unknown=_unknown)

        return obj
