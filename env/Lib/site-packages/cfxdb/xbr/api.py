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
from cfxdb.gen.xbr import Api as ApiGen
from zlmdb import table, MapUuidFlatBuffers, MapBytes16TimestampUuid
from cfxdb import pack_uint256, unpack_uint256


class _ApiGen(ApiGen.Api):
    @classmethod
    def GetRootAsApi(cls, buf, offset):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = _ApiGen()
        x.Init(buf, n + offset)
        return x

    def OidAsBytes(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            _off = self._tab.Vector(o)
            _len = self._tab.VectorLen(o)
            return memoryview(self._tab.Bytes)[_off:_off + _len]
        return None

    def CatalogOidAsBytes(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            _off = self._tab.Vector(o)
            _len = self._tab.VectorLen(o)
            return memoryview(self._tab.Bytes)[_off:_off + _len]
        return None

    def PublishedAsBytes(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(10))
        if o != 0:
            _off = self._tab.Vector(o)
            _len = self._tab.VectorLen(o)
            return memoryview(self._tab.Bytes)[_off:_off + _len]
        return None

    def TidAsBytes(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(16))
        if o != 0:
            _off = self._tab.Vector(o)
            _len = self._tab.VectorLen(o)
            return memoryview(self._tab.Bytes)[_off:_off + _len]
        return None

    def SignatureAsBytes(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(18))
        if o != 0:
            _off = self._tab.Vector(o)
            _len = self._tab.VectorLen(o)
            return memoryview(self._tab.Bytes)[_off:_off + _len]
        return None


class Api(object):
    """
    ``XBRNetwork.Api`` database object.
    """
    def __init__(self, from_fbs=None):
        self._from_fbs = from_fbs

        # [uint8] (uuid);
        self._oid = None

        # [uint8] (uuid);
        self._catalog_oid = None

        # uint64 (timestamp)
        self._timestamp = None

        # [uint8] (uint256)
        self._published = None

        # string (multihash)
        self._schema = None

        # string (multihash)
        self._meta = None

        # [uint8] (ethhash)
        self._tid = None

        # [uint8] (ethsig)
        self._signature = None

    def marshal(self) -> dict:
        obj = {
            'oid': self.oid.bytes if self.oid else None,
            'catalog_oid': self.catalog_oid.bytes if self.catalog_oid else None,
            'timestamp': int(self.timestamp) if self.timestamp else None,
            'published': pack_uint256(self.published) if self.published else None,
            'schema': self.schema,
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
        The unique ID of the api.
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
    def catalog_oid(self) -> uuid.UUID:
        """
        The unique ID of the catalog.
        """
        if self._catalog_oid is None and self._from_fbs:
            if self._from_fbs.CatalogOidLength():
                _oid = self._from_fbs.CatalogOidAsBytes()
                self._oid = uuid.UUID(bytes=bytes(_oid))
        return self._oid

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
    def published(self) -> int:
        """
        Global market sequence number.
        """
        if self._published is None and self._from_fbs:
            if self._from_fbs.PublishedLength():
                _published = self._from_fbs.PublishedAsBytes()
                self._published = unpack_uint256(bytes(_published))
            else:
                self._published = 0
        return self._published

    @published.setter
    def published(self, value: int):
        assert value is None or type(value) == int
        self._published = value

    @property
    def schema(self) -> str:
        """
        The XBR market terms set by the market owner. IPFS Multihash pointing to a ZIP archive file with market documents.
        """
        if self._schema is None and self._from_fbs:
            schema = self._from_fbs.Schema()
            if schema:
                self._schema = schema.decode('utf8')
        return self._schema

    @schema.setter
    def schema(self, value: str):
        assert value is None or type(value) == str
        self._schema = value

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
        return Api(_ApiGen.GetRootAsApi(buf, 0))

    def build(self, builder):

        oid = self.oid.bytes if self.oid else None
        if oid:
            oid = builder.CreateString(oid)

        catalog_oid = self.catalog_oid.bytes if self.catalog_oid else None
        if catalog_oid:
            catalog_oid = builder.CreateString(catalog_oid)

        published = self.published
        if published:
            published = builder.CreateString(pack_uint256(published))

        schema = self.schema
        if schema:
            schema = builder.CreateString(schema)

        meta = self.meta
        if meta:
            meta = builder.CreateString(meta)

        tid = self.tid
        if tid:
            tid = builder.CreateString(tid)

        signature = self.signature
        if signature:
            signature = builder.CreateString(signature)

        ApiGen.ApiStart(builder)

        if oid:
            ApiGen.ApiAddOid(builder, oid)

        if catalog_oid:
            ApiGen.ApiAddCatalogOid(builder, catalog_oid)

        if self.timestamp:
            ApiGen.ApiAddTimestamp(builder, int(self.timestamp))

        if published:
            ApiGen.ApiAddPublished(builder, published)

        if schema:
            ApiGen.ApiAddSchema(builder, schema)

        if meta:
            ApiGen.ApiAddMeta(builder, meta)

        if tid:
            ApiGen.ApiAddTid(builder, tid)

        if signature:
            ApiGen.ApiAddSignature(builder, signature)

        final = ApiGen.ApiEnd(builder)

        return final


@table('9f87bad9-695e-439d-86ad-9e23695d3f67', build=Api.build, cast=Api.cast)
class Apis(MapUuidFlatBuffers):
    """
    Apis table, mapping from ``oid|UUID`` to :class:`cfxdb.xbr.Api`
    """


@table('57ae5d83-57b0-4214-8481-a1853f7faf87')
class IndexApiByCatalog(MapBytes16TimestampUuid):
    """
    Api-by-FbsRepository, index with ``(catalog_oid|bytes[16], created|int) -> api_oid|UUID`` mapping.
    """
