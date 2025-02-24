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
from cfxdb.gen.xbr import Catalog as CatalogGen
from zlmdb import table, MapUuidFlatBuffers, MapBytes20TimestampUuid


class _CatalogGen(CatalogGen.Catalog):
    @classmethod
    def GetRootAsCatalog(cls, buf, offset):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = _CatalogGen()
        x.Init(buf, n + offset)
        return x

    def OidAsBytes(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            _off = self._tab.Vector(o)
            _len = self._tab.VectorLen(o)
            return memoryview(self._tab.Bytes)[_off:_off + _len]
        return None

    def CreatedAsBytes(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(8))
        if o != 0:
            _off = self._tab.Vector(o)
            _len = self._tab.VectorLen(o)
            return memoryview(self._tab.Bytes)[_off:_off + _len]
        return None

    def OwnerAsBytes(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(12))
        if o != 0:
            _off = self._tab.Vector(o)
            _len = self._tab.VectorLen(o)
            return memoryview(self._tab.Bytes)[_off:_off + _len]
        return None

    def TidAsBytes(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(18))
        if o != 0:
            _off = self._tab.Vector(o)
            _len = self._tab.VectorLen(o)
            return memoryview(self._tab.Bytes)[_off:_off + _len]
        return None

    def SignatureAsBytes(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(20))
        if o != 0:
            _off = self._tab.Vector(o)
            _len = self._tab.VectorLen(o)
            return memoryview(self._tab.Bytes)[_off:_off + _len]
        return None


class Catalog(object):
    """
    ``XBRNetwork.FbsRepository`` database object.
    """
    def __init__(self, from_fbs=None):
        self._from_fbs = from_fbs

        # [uint8] (uuid);
        self._oid = None

        # uint64 (timestamp)
        self._timestamp = None

        # uint32
        self._seq = None

        # [uint8] (address)
        self._owner = None

        # string (multihash)
        self._terms = None

        # string (multihash)
        self._meta = None

        # [uint8] (ethhash)
        self._tid = None

        # [uint8] (ethsig)
        self._signature = None

    def marshal(self) -> dict:
        obj = {
            'oid': self.oid.bytes if self.oid else None,
            'timestamp': int(self.timestamp) if self.timestamp else None,
            'seq': self.seq,
            'owner': bytes(self.owner) if self.owner else None,
            'terms': self.terms,
            'meta': self.meta,
            'tid': bytes(self.tid) if self.tid else None,
            'signature': bytes(self.signature) if self.signature else None,
        }
        return obj

    def __str__(self):
        return '\n{}\n'.format(pprint.pformat(self.marshal()))

    @property
    def oid(self) -> uuid.UUID:
        """
        The unique ID of the market.
        """
        if self._oid is None and self._from_fbs:
            if self._from_fbs.OidLength():
                _oid = self._from_fbs.OidAsBytes()
                self._oid = uuid.UUID(bytes=bytes(_oid))
        return self._oid

    @oid.setter
    def oid(self, value: uuid.UUID):
        assert value is None or isinstance(value, uuid.UUID)
        self._oid = value

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
    def seq(self) -> int:
        """
        Global market sequence number.
        """
        if self._seq is None and self._from_fbs:
            self._seq = self._from_fbs.Seq()
        return self._seq or 0

    @seq.setter
    def seq(self, value: int):
        assert value is None or type(value) == int
        self._seq = value

    @property
    def owner(self) -> bytes:
        """
        FbsRepository owner.
        """
        if self._owner is None and self._from_fbs:
            if self._from_fbs.OwnerLength():
                self._owner = self._from_fbs.OwnerAsBytes()
        return self._owner

    @owner.setter
    def owner(self, value: bytes):
        assert value is None or (type(value) == bytes and len(value) == 20)
        self._owner = value

    @property
    def terms(self) -> str:
        """
        The XBR market terms set by the market owner. IPFS Multihash pointing to a ZIP archive file with market documents.
        """
        if self._terms is None and self._from_fbs:
            terms = self._from_fbs.Terms()
            if terms:
                self._terms = terms.decode('utf8')
        return self._terms

    @terms.setter
    def terms(self, value: str):
        assert value is None or type(value) == str
        self._terms = value

    @property
    def meta(self) -> str:
        """
        The XBR market metadata published by the market owner. IPFS Multihash pointing to a RDF/Turtle file with market metadata.
        """
        if self._meta is None and self._from_fbs:
            meta = self._from_fbs.Meta()
            if meta:
                self._meta = meta.decode('utf8')
        return self._meta

    @meta.setter
    def meta(self, value):
        assert value is None or type(value) == str
        self._meta = value

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

    @staticmethod
    def cast(buf):
        return Catalog(_CatalogGen.GetRootAsCatalog(buf, 0))

    def build(self, builder):

        oid = self.oid.bytes if self.oid else None
        if oid:
            oid = builder.CreateString(oid)

        terms = self.terms
        if terms:
            terms = builder.CreateString(terms)

        meta = self.meta
        if meta:
            meta = builder.CreateString(meta)

        tid = self.tid
        if tid:
            tid = builder.CreateString(tid)

        signature = self.signature
        if signature:
            signature = builder.CreateString(signature)

        owner = self.owner
        if owner:
            owner = builder.CreateString(owner)

        CatalogGen.CatalogStart(builder)

        if oid:
            CatalogGen.CatalogAddOid(builder, oid)

        if self.timestamp:
            CatalogGen.CatalogAddTimestamp(builder, int(self.timestamp))

        if self.seq:
            CatalogGen.CatalogAddSeq(builder, self.seq)

        if terms:
            CatalogGen.CatalogAddTerms(builder, terms)

        if meta:
            CatalogGen.CatalogAddMeta(builder, meta)

        if tid:
            CatalogGen.CatalogAddTid(builder, tid)

        if signature:
            CatalogGen.CatalogAddSignature(builder, signature)

        if owner:
            CatalogGen.CatalogAddOwner(builder, owner)

        final = CatalogGen.CatalogEnd(builder)

        return final


@table('60ba3189-d127-4522-bfbc-ed416bf7233c', build=Catalog.build, cast=Catalog.cast)
class Catalogs(MapUuidFlatBuffers):
    """
    Catalogs table, mapping from ``oid|UUID`` to :class:`cfxdb.xbr.FbsRepository`
    """


@table('2e331469-68f8-4b1b-a1b9-904f7e29dbc5')
class IndexCatalogsByOwner(MapBytes20TimestampUuid):
    """
    Catalogs-by-owner index with ``(owner_adr|bytes[20], created|int) -> catalog_id|UUID`` mapping.
    """
