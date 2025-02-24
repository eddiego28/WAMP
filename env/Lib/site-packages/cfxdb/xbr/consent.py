##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################
import pprint
import uuid

import flatbuffers
import numpy as np
from cfxdb import pack_uint256, unpack_uint256
from cfxdb.gen.xbr import Consent as ConsentGen
from zlmdb import table, MapBytes20TimestampUuid, MapUuidBytes20Bytes20Uint8UuidFlatBuffers


class _ConsentGen(ConsentGen.Consent):
    @classmethod
    def GetRootAsConsent(cls, buf, offset):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = _ConsentGen()
        x.Init(buf, n + offset)
        return x

    def _as_bytes(self, offet):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(offet))
        if o != 0:
            _off = self._tab.Vector(o)
            _len = self._tab.VectorLen(o)
            return memoryview(self._tab.Bytes)[_off:_off + _len]
        return None

    def MarketOidAsBytes(self):
        return self._as_bytes(4)

    def MemberAsBytes(self):
        return self._as_bytes(6)

    def DelegateAsBytes(self):
        return self._as_bytes(8)

    def CatalogOidAsBytes(self):
        return self._as_bytes(12)

    def UpdatedAsBytes(self):
        return self._as_bytes(16)

    def TidAsBytes(self):
        return self._as_bytes(22)

    def SignatureAsBytes(self):
        return self._as_bytes(24)


class Consent(object):
    """
    ``XBRNetwork.Consent`` database object.
    """
    def __init__(self, from_fbs=None):
        self._from_fbs = from_fbs

        # [uint8] (uuid);
        self._market_oid = None

        # [uint8] (address)
        self._member = None

        # [uint8] (address)
        self._delegate = None

        # [uint8] ActorType
        self._delegate_type = None

        # [uint8] (uuid);
        self._catalog_oid = None

        # uint64 (timestamp)
        self._timestamp = None

        # [uint8] (uint256)
        self._updated = None

        # bool
        self._consent = None

        # string
        self._service_prefix = None

        # [uint8] (ethhash)
        self._tid = None

        # [uint8] (ethsig)
        self._signature = None

        # bool
        self._synced = None

    def marshal(self) -> dict:
        obj = {
            'market_oid': self.market_oid.bytes if self.market_oid else None,
            'member': bytes(self.member) if self.member else None,
            'delegate': bytes(self.delegate) if self.delegate else None,
            'delegate_type': int(self.delegate_type) if self.delegate_type else None,
            'catalog_oid': self.catalog_oid.bytes if self.catalog_oid else None,
            'timestamp': int(self.timestamp) if self.timestamp else None,
            'updated': pack_uint256(self.updated) if self.updated else None,
            'consent': self.consent,
            'service_prefix': self.service_prefix if self.service_prefix else None,
            'tid': bytes(self.tid) if self.tid else None,
            'signature': bytes(self.signature) if self.signature else None,
            'synced': self.synced,
        }
        return obj

    def __str__(self):
        return '\n{}\n'.format(pprint.pformat(self.marshal()))

    @property
    def market_oid(self) -> uuid.UUID:
        """
        The unique ID of the market.
        """
        if self._market_oid is None and self._from_fbs:
            if self._from_fbs.MarketOidLength():
                _market_oid = self._from_fbs.MarketOidAsBytes()
                self._market_oid = uuid.UUID(bytes=bytes(_market_oid))
        return self._market_oid

    @market_oid.setter
    def market_oid(self, value: uuid.UUID):
        assert value is None or isinstance(value, uuid.UUID)
        self._market_oid = value

    @property
    def member(self) -> bytes:
        """
        The unique ID of the market.
        """
        if self._member is None and self._from_fbs:
            if self._from_fbs.MemberLength():
                self._member = self._from_fbs.MemberAsBytes()
        return self._member

    @member.setter
    def member(self, value: bytes):
        assert value is None or (type(value) == bytes and len(value) == 20)
        self._member = value

    @property
    def delegate(self) -> bytes:
        """
        The unique ID of the market.
        """
        if self._delegate is None and self._from_fbs:
            if self._from_fbs.DelegateLength():
                self._delegate = self._from_fbs.DelegateAsBytes()
        return self._delegate

    @delegate.setter
    def delegate(self, value: bytes):
        assert value is None or (type(value) == bytes and len(value) == 20)
        self._delegate = value

    @property
    def delegate_type(self) -> int:
        """
        The unique ID of the market.
        """
        if self._delegate_type is None and self._from_fbs:
            self._delegate_type = self._from_fbs.DelegateType()
        return self._delegate_type

    @delegate_type.setter
    def delegate_type(self, value: int):
        assert value is None or type(value) == int
        self._delegate_type = value

    @property
    def catalog_oid(self) -> uuid.UUID:
        """
        The unique ID of the catalog.
        """
        if self._catalog_oid is None and self._from_fbs:
            if self._from_fbs.CatalogOidLength():
                _catalog_oid = self._from_fbs.CatalogOidAsBytes()
                self._catalog_oid = uuid.UUID(bytes=bytes(_catalog_oid))
        return self._catalog_oid

    @catalog_oid.setter
    def catalog_oid(self, value: uuid.UUID):
        assert value is None or isinstance(value, uuid.UUID)
        self._catalog_oid = value

    @property
    def timestamp(self) -> np.datetime64:
        """
        Database transaction time (epoch time in ns) of insert or last update.
        """
        if self._timestamp is None and self._from_fbs:
            self._timestamp = np.datetime64(self._from_fbs.Timestamp(), 'ns')
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value: np.datetime64):
        assert value is None or isinstance(value, np.datetime64)
        self._timestamp = value

    @property
    def updated(self) -> int:
        """
        The amount of XBR tokens a XBR provider joining the market must deposit.
        """
        if self._updated is None and self._from_fbs:
            if self._from_fbs.UpdatedLength():
                _updated = self._from_fbs.UpdatedAsBytes()
                self._updated = unpack_uint256(bytes(_updated))
            else:
                self._updated = 0
        return self._updated

    @updated.setter
    def updated(self, value: int):
        assert value is None or type(value) == int
        self._updated = value

    @property
    def consent(self) -> bool:
        """
        Whether we have the consent
        """
        if self._consent is None and self._from_fbs:
            self._consent = self._from_fbs.Consent()
        return self._consent

    @consent.setter
    def consent(self, value: bool):
        assert type(value) == bool
        self._consent = value

    @property
    def service_prefix(self) -> str:
        if self._service_prefix is None and self._from_fbs:
            service_prefix = self._from_fbs.ServicePrefix()
            if service_prefix:
                self.service_prefix = service_prefix.decode('utf8')
        return self._service_prefix

    @service_prefix.setter
    def service_prefix(self, value):
        assert value is None or type(value) == str
        self._service_prefix = value

    @property
    def tid(self) -> bytes:
        """
        Transaction hash of the transaction this change was committed to the blockchain under.
        """
        if self._tid is None and self._from_fbs:
            if self._from_fbs.TidLength():
                self._tid = self._from_fbs.TidAsBytes()
        return self._tid

    @tid.setter
    def tid(self, value: bytes):
        assert value is None or (type(value) == bytes and len(value) == 32)
        self._tid = value

    @property
    def signature(self) -> bytes:
        """
        When signed off-chain and submitted via ``XBRMarket.createMarketFor``.
        """
        if self._signature is None and self._from_fbs:
            if self._from_fbs.SignatureLength():
                self._signature = self._from_fbs.SignatureAsBytes()
        return self._signature

    @signature.setter
    def signature(self, value: bytes):
        assert value is None or (type(value) == bytes and len(value) == 65)
        self._signature = value

    @property
    def synced(self) -> bool:
        """
        Whether the consent is synced with blockchain
        """
        if self._synced is None and self._from_fbs:
            self._synced = self._from_fbs.Synced()
        return self._synced

    @synced.setter
    def synced(self, value: bool):
        assert type(value) == bool
        self._synced = value

    @staticmethod
    def cast(buf):
        return Consent(_ConsentGen.GetRootAsConsent(buf, 0))

    def build(self, builder):

        market_oid = self.market_oid.bytes if self.market_oid else None
        if market_oid:
            market_oid = builder.CreateString(market_oid)

        member = self.member
        if member:
            member = builder.CreateString(member)

        delegate = self.delegate
        if delegate:
            delegate = builder.CreateString(delegate)

        delegate_type = self.delegate_type

        catalog_oid = self.catalog_oid.bytes if self.catalog_oid else None
        if catalog_oid:
            catalog_oid = builder.CreateString(catalog_oid)

        updated = self.updated
        if updated:
            updated = builder.CreateString(pack_uint256(updated))

        service_prefix = self.service_prefix
        if service_prefix:
            service_prefix = builder.CreateString(service_prefix)

        tid = self.tid
        if tid:
            tid = builder.CreateString(tid)

        signature = self.signature
        if signature:
            signature = builder.CreateString(signature)

        ConsentGen.ConsentStart(builder)

        if market_oid:
            ConsentGen.ConsentAddMarketOid(builder, market_oid)

        if member:
            ConsentGen.ConsentAddMember(builder, member)

        if delegate:
            ConsentGen.ConsentAddDelegate(builder, delegate)

        if delegate_type:
            ConsentGen.ConsentAddDelegateType(builder, delegate_type)

        if catalog_oid:
            ConsentGen.ConsentAddCatalogOid(builder, catalog_oid)

        if self.timestamp:
            ConsentGen.ConsentAddTimestamp(builder, int(self.timestamp))

        if updated:
            ConsentGen.ConsentAddUpdated(builder, updated)

        ConsentGen.ConsentAddConsent(builder, self.consent)
        ConsentGen.ConsentAddSynced(builder, self.synced or False)

        if service_prefix:
            ConsentGen.ConsentAddServicePrefix(builder, service_prefix)

        if tid:
            ConsentGen.ConsentAddTid(builder, tid)

        if signature:
            ConsentGen.ConsentAddSignature(builder, signature)

        final = ConsentGen.ConsentEnd(builder)

        return final


@table('8b10071b-5b2a-478f-8101-52dfbaf0760a', build=Consent.build, cast=Consent.cast)
class Consents(MapUuidBytes20Bytes20Uint8UuidFlatBuffers):
    """
    Consents table
    """


@table('7cdac5f2-bddf-4fda-8e3c-21938a0c3667')
class IndexConsentByMemberAddress(MapBytes20TimestampUuid):
    """
    Consent-by-member-address index with ``(member_adr|bytes[20], timestamp|int) -> consent_oid|UUID`` mapping.
    """
