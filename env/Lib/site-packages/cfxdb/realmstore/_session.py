##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################

import uuid
import cbor2
from typing import Optional, Dict, Any
import pprint

import flatbuffers
import numpy as np

from zlmdb import table, MapUuidFlatBuffers, MapUint64TimestampUuid
from cfxdb.gen.realmstore import Session as SessionGen


class _SessionGen(SessionGen.Session):
    @classmethod
    def GetRootAs(cls, buf, offset=0):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = _SessionGen()
        x.Init(buf, n + offset)
        return x

    def ArealmOidAsBytes(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            _off = self._tab.Vector(o)
            _len = self._tab.VectorLen(o)
            return memoryview(self._tab.Bytes)[_off:_off + _len]
        return None

    def OidAsBytes(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            _off = self._tab.Vector(o)
            _len = self._tab.VectorLen(o)
            return memoryview(self._tab.Bytes)[_off:_off + _len]
        return None

    def NodeOidAsBytes(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(14))
        if o != 0:
            _off = self._tab.Vector(o)
            _len = self._tab.VectorLen(o)
            return memoryview(self._tab.Bytes)[_off:_off + _len]
        return None

    def TransportAsBytes(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(22))
        if o != 0:
            _off = self._tab.Vector(o)
            _len = self._tab.VectorLen(o)
            return memoryview(self._tab.Bytes)[_off:_off + _len]
        return None

    def ProxyNodeOidAsBytes(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(24))
        if o != 0:
            _off = self._tab.Vector(o)
            _len = self._tab.VectorLen(o)
            return memoryview(self._tab.Bytes)[_off:_off + _len]
        return None

    def ProxyTransportAsBytes(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(32))
        if o != 0:
            _off = self._tab.Vector(o)
            _len = self._tab.VectorLen(o)
            return memoryview(self._tab.Bytes)[_off:_off + _len]
        return None

    def AuthextraAsBytes(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(44))
        if o != 0:
            _off = self._tab.Vector(o)
            _len = self._tab.VectorLen(o)
            return memoryview(self._tab.Bytes)[_off:_off + _len]
        return None


class Session(object):
    """
    Persisted session database object.
    """

    __slots__ = (
        '_from_fbs',
        '_arealm_oid',
        '_oid',
        '_session',
        '_joined_at',
        '_left_at',
        '_node_oid',
        '_node_authid',
        '_worker_name',
        '_worker_pid',
        '_transport',
        '_proxy_node_oid',
        '_proxy_node_authid',
        '_proxy_worker_name',
        '_proxy_worker_pid',
        '_proxy_transport',
        '_realm',
        '_authid',
        '_authrole',
        '_authmethod',
        '_authprovider',
        '_authextra',
    )

    def __init__(self, from_fbs: Optional[_SessionGen] = None):
        self._from_fbs = from_fbs

        # [uint8] (uuid)
        self._arealm_oid: Optional[uuid.UUID] = None

        # [uint8] (uuid)
        self._oid: Optional[uuid.UUID] = None

        # uint64
        self._session: Optional[int] = None

        # uint64 (timestamp)
        self._joined_at: Optional[np.datetime64] = None

        # uint64 (timestamp)
        self._left_at: Optional[np.datetime64] = None

        # [uint8] (uuid)
        self._node_oid: Optional[uuid.UUID] = None

        # string
        self._node_authid: Optional[str] = None

        # string
        self._worker_name: Optional[str] = None

        # int32
        self._worker_pid: Optional[int] = None

        # [uint8] (cbor)
        self._transport: Optional[Dict[str, Any]] = None

        # [uint8] (uuid)
        self._proxy_node_oid: Optional[uuid.UUID] = None

        # string
        self._proxy_node_authid: Optional[str] = None

        # string
        self._proxy_worker_name: Optional[str] = None

        # int32
        self._proxy_worker_pid: Optional[int] = None

        # [uint8] (cbor)
        self._proxy_transport: Optional[Dict[str, Any]] = None

        # string
        self._realm: Optional[str] = None

        # string
        self._authid: Optional[str] = None

        # string
        self._authrole: Optional[str] = None

        # string
        self._authmethod: Optional[str] = None

        # string
        self._authprovider: Optional[str] = None

        # [uint8] (cbor)
        self._authextra: Optional[Dict[str, Any]] = None

    def marshal(self):
        obj = {
            'arealm_oid': self.arealm_oid.bytes if self.arealm_oid else None,
            'oid': self.oid.bytes if self.oid else None,
            'session': self.session,
            'joined_at': int(self.joined_at) if self.joined_at else None,
            'left_at': int(self.left_at) if self.left_at else None,
            'node_oid': self.node_oid.bytes if self.node_oid else None,
            'node_authid': self.node_authid,
            'worker_name': self.worker_name,
            'worker_pid': self.worker_pid,
            'transport': self.transport,
            'proxy_node_oid': self.proxy_node_oid.bytes if self.proxy_node_oid else None,
            'proxy_node_authid': self.proxy_node_authid,
            'proxy_worker_name': self.proxy_worker_name,
            'proxy_worker_pid': self.proxy_worker_pid,
            'proxy_transport': self.proxy_transport,
            'realm': self.realm,
            'authid': self.authid,
            'authrole': self.authrole,
            'authmethod': self.authmethod,
            'authprovider': self.authprovider,
            'authextra': self.authextra,
        }
        return obj

    def __str__(self):
        return '\n{}\n'.format(pprint.pformat(self.marshal()))

    @property
    def arealm_oid(self) -> Optional[uuid.UUID]:
        """
        OID of the application realm this session is/was joined on.
        """
        if self._arealm_oid is None and self._from_fbs:
            if self._from_fbs.ArealmOidLength():
                _arealm_oid = self._from_fbs.ArealmOidAsBytes()
                self._arealm_oid = uuid.UUID(bytes=bytes(_arealm_oid))
        return self._arealm_oid

    @arealm_oid.setter
    def arealm_oid(self, value: Optional[uuid.UUID]):
        assert value is None or isinstance(value, uuid.UUID)
        self._arealm_oid = value

    @property
    def oid(self) -> Optional[uuid.UUID]:
        """
        Unlimited time, globally unique, long-term OID of this session. The pair of WAMP session ID and join time ``(session, joined_at)`` bidirectionally maps to session ``oid``.
        """
        if self._oid is None and self._from_fbs:
            if self._from_fbs.OidLength():
                _oid = self._from_fbs.OidAsBytes()
                self._oid = uuid.UUID(bytes=bytes(_oid))
        return self._oid

    @oid.setter
    def oid(self, value: Optional[uuid.UUID]):
        assert value is None or isinstance(value, uuid.UUID)
        self._oid = value

    @property
    def session(self) -> Optional[int]:
        """
        The WAMP session_id of the session.
        """
        if self._session is None and self._from_fbs:
            self._session = self._from_fbs.Session()
        return self._session

    @session.setter
    def session(self, value: Optional[int]):
        assert value is None or type(value) == int
        self._session = value

    @property
    def joined_at(self) -> Optional[np.datetime64]:
        """
        Timestamp when the session was joined by the router. Epoch time in ns.
        """
        if self._joined_at is None and self._from_fbs:
            self._joined_at = np.datetime64(self._from_fbs.JoinedAt(), 'ns')
        return self._joined_at

    @joined_at.setter
    def joined_at(self, value: Optional[np.datetime64]):
        assert value is None or isinstance(value, np.datetime64)
        self._joined_at = value

    @property
    def left_at(self) -> Optional[np.datetime64]:
        """
        Timestamp when the session left the router. Epoch time in ns.
        """
        if self._left_at is None and self._from_fbs:
            self._left_at = np.datetime64(self._from_fbs.LeftAt(), 'ns')
        return self._left_at

    @left_at.setter
    def left_at(self, value: Optional[np.datetime64]):
        assert value is None or isinstance(value, np.datetime64)
        self._left_at = value

    @property
    def node_oid(self) -> Optional[uuid.UUID]:
        """
        OID of the node of the router worker hosting this session.
        """
        if self._node_oid is None and self._from_fbs:
            if self._from_fbs.NodeOidLength():
                _node_oid = self._from_fbs.NodeOidAsBytes()
                self._node_oid = uuid.UUID(bytes=bytes(_node_oid))
        return self._node_oid

    @node_oid.setter
    def node_oid(self, value: Optional[uuid.UUID]):
        assert value is None or isinstance(value, uuid.UUID)
        self._node_oid = value

    @property
    def node_authid(self) -> Optional[str]:
        """
        Name (management realm WAMP authid) of the node of the router worker hosting this session.
        """
        if self._node_authid is None and self._from_fbs:
            _node_authid = self._from_fbs.NodeAuthid()
            if _node_authid:
                self._node_authid = _node_authid.decode('utf8')
        return self._node_authid

    @node_authid.setter
    def node_authid(self, value: Optional[str]):
        self._node_authid = value

    @property
    def worker_name(self) -> Optional[str]:
        """
        Local worker name of the router worker hosting this session.
        """
        if self._worker_name is None and self._from_fbs:
            _worker_name = self._from_fbs.WorkerName()
            if _worker_name:
                self._worker_name = _worker_name.decode('utf8')
        return self._worker_name

    @worker_name.setter
    def worker_name(self, value: Optional[str]):
        self._worker_name = value

    @property
    def worker_pid(self) -> Optional[int]:
        """
        Local worker PID of the router worker hosting this session.
        """
        if self._worker_pid is None and self._from_fbs:
            self._worker_pid = self._from_fbs.WorkerPid()
        return self._worker_pid

    @worker_pid.setter
    def worker_pid(self, value: Optional[int]):
        self._worker_pid = value

    @property
    def transport(self) -> Optional[Dict[str, Any]]:
        """
        Session transport information.
        """
        if self._transport is None and self._from_fbs:
            _transport = self._from_fbs.TransportAsBytes()
            if _transport:
                self._transport = cbor2.loads(_transport)
            else:
                self._transport = {}
        return self._transport

    @transport.setter
    def transport(self, value: Optional[Dict[str, Any]]):
        assert value is None or type(value) == dict
        self._transport = value

    @property
    def proxy_node_oid(self) -> Optional[uuid.UUID]:
        """
        From proxy (in proxy-router cluster setups): OID of the node of the proxy worker hosting this session.
        """
        if self._proxy_node_oid is None and self._from_fbs:
            if self._from_fbs.ProxyNodeOidLength():
                _proxy_node_oid = self._from_fbs.ProxyNodeOidAsBytes()
                self._proxy_node_oid = uuid.UUID(bytes=bytes(_proxy_node_oid))
        return self._proxy_node_oid

    @proxy_node_oid.setter
    def proxy_node_oid(self, value: Optional[uuid.UUID]):
        assert value is None or isinstance(value, uuid.UUID)
        self._proxy_node_oid = value

    @property
    def proxy_node_authid(self) -> Optional[str]:
        """
        From proxy (in proxy-router cluster setups): Name (management realm WAMP authid) of the node of the proxy worker hosting this session.
        """
        if self._proxy_node_authid is None and self._from_fbs:
            _proxy_node_authid = self._from_fbs.ProxyNodeAuthid()
            if _proxy_node_authid:
                self._proxy_node_authid = _proxy_node_authid.decode('utf8')
        return self._proxy_node_authid

    @proxy_node_authid.setter
    def proxy_node_authid(self, value: Optional[str]):
        self._proxy_node_authid = value

    @property
    def proxy_worker_name(self) -> Optional[str]:
        """
        From proxy (in proxy-router cluster setups): Local worker name of the proxy worker hosting this session.
        """
        if self._proxy_worker_name is None and self._from_fbs:
            _proxy_worker_name = self._from_fbs.ProxyWorkerName()
            if _proxy_worker_name:
                self._proxy_worker_name = _proxy_worker_name.decode('utf8')
        return self._proxy_worker_name

    @proxy_worker_name.setter
    def proxy_worker_name(self, value: Optional[str]):
        self._proxy_worker_name = value

    @property
    def proxy_worker_pid(self) -> Optional[int]:
        """
        From proxy (in proxy-router cluster setups): Local worker PID of the proxy worker hosting this session.
        """
        if self._proxy_worker_pid is None and self._from_fbs:
            self._proxy_worker_pid = self._from_fbs.ProxyWorkerPid()
        return self._proxy_worker_pid

    @proxy_worker_pid.setter
    def proxy_worker_pid(self, value: Optional[int]):
        self._proxy_worker_pid = value

    @property
    def proxy_transport(self) -> Optional[Dict[str, Any]]:
        """
        From proxy (in proxy-router cluster setups): Session transport information, the transport from the proxy to the backend router.
        """
        if self._proxy_transport is None and self._from_fbs:
            _proxy_transport = self._from_fbs.ProxyTransportAsBytes()
            if _proxy_transport:
                self._proxy_transport = cbor2.loads(_proxy_transport)
            else:
                self._proxy_transport = {}
        return self._proxy_transport

    @proxy_transport.setter
    def proxy_transport(self, value: Optional[Dict[str, Any]]):
        assert value is None or type(value) == dict
        self._proxy_transport = value

    @property
    def realm(self) -> Optional[str]:
        """
        The WAMP realm the session is/was joined on.
        """
        if self._realm is None and self._from_fbs:
            self._realm = self._from_fbs.Realm().decode('utf8')
        return self._realm

    @realm.setter
    def realm(self, value: Optional[str]):
        assert value is None or type(value) == str
        self._realm = value

    @property
    def authid(self) -> Optional[str]:
        """
        The WAMP authid the session was authenticated under.
        """
        if self._authid is None and self._from_fbs:
            _authid = self._from_fbs.Authid()
            if _authid:
                self._authid = _authid.decode('utf8')
        return self._authid

    @authid.setter
    def authid(self, value: Optional[str]):
        self._authid = value

    @property
    def authrole(self) -> Optional[str]:
        """
        The WAMP authrole the session was authenticated under.
        """
        if self._authrole is None and self._from_fbs:
            _authrole = self._from_fbs.Authrole()
            if _authrole:
                self._authrole = _authrole.decode('utf8')
        return self._authrole

    @authrole.setter
    def authrole(self, value: Optional[str]):
        self._authrole = value

    @property
    def authmethod(self) -> Optional[str]:
        """
        The WAMP authmethod uses to authenticate the session.
        """
        if self._authmethod is None and self._from_fbs:
            _authmethod = self._from_fbs.Authmethod()
            if _authmethod:
                self._authmethod = _authmethod.decode('utf8')
        return self._authmethod

    @authmethod.setter
    def authmethod(self, value: Optional[str]):
        self._authmethod = value

    @property
    def authprovider(self) -> Optional[str]:
        """
        The WAMP authprovider that was handling the session authentication.
        """
        if self._authprovider is None and self._from_fbs:
            _authprovider = self._from_fbs.Authprovider()
            if _authprovider:
                self._authprovider = _authprovider.decode('utf8')
        return self._authprovider

    @authprovider.setter
    def authprovider(self, value: Optional[str]):
        self._authprovider = value

    @property
    def authextra(self) -> Optional[Dict[str, Any]]:
        """
        The WAMP authextra as provided to the authenticated session.
        """
        if self._authextra is None and self._from_fbs:
            _authextra = self._from_fbs.AuthextraAsBytes()
            if _authextra:
                self._authextra = cbor2.loads(_authextra)
            else:
                self._authextra = {}
        return self._authextra

    @authextra.setter
    def authextra(self, value: Optional[Dict[str, Any]]):
        assert value is None or type(value) == dict
        self._authextra = value

    @staticmethod
    def cast(buf) -> 'Session':
        return Session(_SessionGen.GetRootAsSession(buf, 0))

    def build(self, builder):

        arealm_oid = self.arealm_oid.bytes if self.arealm_oid else None
        if arealm_oid:
            arealm_oid = builder.CreateString(arealm_oid)

        oid = self.oid.bytes if self.oid else None
        if oid:
            oid = builder.CreateString(oid)

        node_oid = self.node_oid.bytes if self.node_oid else None
        if node_oid:
            node_oid = builder.CreateString(node_oid)

        node_authid = self.node_authid
        if node_authid:
            node_authid = builder.CreateString(node_authid)

        worker_name = self.worker_name
        if worker_name:
            worker_name = builder.CreateString(worker_name)

        transport = self.transport
        if transport:
            transport = builder.CreateString(cbor2.dumps(transport))

        proxy_node_oid = self.proxy_node_oid.bytes if self.proxy_node_oid else None
        if proxy_node_oid:
            proxy_node_oid = builder.CreateString(proxy_node_oid)

        proxy_node_authid = self.proxy_node_authid
        if proxy_node_authid:
            proxy_node_authid = builder.CreateString(proxy_node_authid)

        proxy_worker_name = self.proxy_worker_name
        if proxy_worker_name:
            proxy_worker_name = builder.CreateString(proxy_worker_name)

        proxy_transport = self.proxy_transport
        if proxy_transport:
            proxy_transport = builder.CreateString(cbor2.dumps(proxy_transport))

        realm = self.realm
        if realm:
            realm = builder.CreateString(realm)

        authid = self.authid
        if authid:
            authid = builder.CreateString(authid)

        authrole = self.authrole
        if authrole:
            authrole = builder.CreateString(authrole)

        authmethod = self.authmethod
        if authmethod:
            authmethod = builder.CreateString(authmethod)

        authprovider = self.authprovider
        if authprovider:
            authprovider = builder.CreateString(authprovider)

        authextra = self.authextra
        if authextra:
            authextra = builder.CreateString(cbor2.dumps(authextra))

        SessionGen.SessionStart(builder)

        if arealm_oid:
            SessionGen.SessionAddArealmOid(builder, arealm_oid)

        if oid:
            SessionGen.SessionAddOid(builder, oid)

        if self.session:
            SessionGen.SessionAddSession(builder, self.session)

        if self.joined_at:
            SessionGen.SessionAddJoinedAt(builder, int(self.joined_at))

        if self.left_at:
            SessionGen.SessionAddLeftAt(builder, int(self.left_at))

        if node_oid:
            SessionGen.SessionAddNodeOid(builder, node_oid)

        if node_authid:
            SessionGen.SessionAddNodeAuthid(builder, node_authid)

        if worker_name:
            SessionGen.SessionAddWorkerName(builder, worker_name)

        if self.worker_pid:
            SessionGen.SessionAddWorkerPid(builder, self.worker_pid)

        if transport:
            SessionGen.SessionAddTransport(builder, transport)

        if proxy_node_oid:
            SessionGen.SessionAddProxyNodeOid(builder, proxy_node_oid)

        if proxy_node_authid:
            SessionGen.SessionAddProxyNodeAuthid(builder, proxy_node_authid)

        if proxy_worker_name:
            SessionGen.SessionAddProxyWorkerName(builder, proxy_worker_name)

        if self.proxy_worker_pid:
            SessionGen.SessionAddProxyWorkerPid(builder, self.proxy_worker_pid)

        if proxy_transport:
            SessionGen.SessionAddProxyTransport(builder, proxy_transport)

        if realm:
            SessionGen.SessionAddRealm(builder, realm)

        if authid:
            SessionGen.SessionAddAuthid(builder, authid)

        if authrole:
            SessionGen.SessionAddAuthrole(builder, authrole)

        if authmethod:
            SessionGen.SessionAddAuthmethod(builder, authmethod)

        if authprovider:
            SessionGen.SessionAddAuthprovider(builder, authprovider)

        if authextra:
            SessionGen.SessionAddAuthextra(builder, authextra)

        final = SessionGen.SessionEnd(builder)

        return final


@table('403ecc06-f564-4ea9-92f2-c4c13bd2ba5a', build=Session.build, cast=Session.cast)
class Sessions(MapUuidFlatBuffers):
    """
    Persisted session information table.

    Map :class:`zlmdb.MapUuidFlatBuffers` from ``session_oid`` to :class:`cfxdb.realmstore.Session`
    """


@table('0ea1ea1a-45f2-4352-a4a0-1fafff099c96')
class IndexSessionsBySessionId(MapUint64TimestampUuid):
    """
    Index: ``(sessionid, joined_at) -> session_oid``
    """
