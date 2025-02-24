##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################

from typing import Optional, List
import pprint
from uuid import UUID

import numpy as np

from cfxdb.mrealm.cluster import Cluster


class WebCluster(Cluster):
    """
    Web cluster database configuration object.
    """
    def __init__(self,
                 oid: Optional[UUID] = None,
                 label: Optional[str] = None,
                 description: Optional[str] = None,
                 tags: Optional[List[str]] = None,
                 name: Optional[str] = None,
                 status: Optional[int] = None,
                 owner_oid: Optional[UUID] = None,
                 changed: Optional[np.datetime64] = None,
                 tcp_version: Optional[int] = None,
                 tcp_port: Optional[int] = None,
                 tcp_shared: Optional[bool] = None,
                 tcp_interface: Optional[str] = None,
                 tcp_backlog: Optional[int] = None,
                 tls_key: Optional[str] = None,
                 tls_certificate: Optional[str] = None,
                 tls_chain_certificates: Optional[List[str]] = None,
                 tls_ca_certificates: Optional[List[str]] = None,
                 tls_dhparam: Optional[str] = None,
                 tls_ciphers: Optional[str] = None,
                 http_client_timeout: Optional[int] = None,
                 http_hsts: Optional[bool] = None,
                 http_hsts_max_age: Optional[int] = None,
                 http_access_log: Optional[bool] = None,
                 http_display_tracebacks: Optional[bool] = None,
                 _unknown=None):
        """

        :param oid: Object ID of node

        :param label: Optional user label of node

        :param description: Optional user description of node

        :param tags: Optional list of user tags on node

        :param tcp_version: IP version, either 4 for 6

        :param tcp_port: IP listening port

        :param tcp_shared: enable TCP port sharing

        :param tcp_interface: listen on this interface

        :param tcp_backlog: TCP accept backlog queue size

        :param tls_key: TLS server private key to use

        :param tls_certificate: TLS server certificate to use

        :param tls_chain_certificates: TLS certificate chain

        :param tls_ca_certificates: CA certificates to use

        :param tls_dhparam: DH parameter file

        :param tls_ciphers: Ciphers list

        :param http_client_timeout: HTTP client inactivity timeout

        :param http_hsts: enable HTTP strict transport security (HSTS)

        :param http_hsts_max_age: HSTS maximum age to announce

        :param http_access_log: enable Web request access logging

        :param http_display_tracebacks: enable tracebacks when running into Web errors
        """
        Cluster.__init__(self,
                         oid=oid,
                         label=label,
                         description=description,
                         tags=tags,
                         name=name,
                         status=status,
                         owner_oid=owner_oid,
                         changed=changed,
                         _unknown=_unknown)
        self.tcp_version = tcp_version
        self.tcp_port = tcp_port
        self.tcp_shared = tcp_shared
        self.tcp_interface = tcp_interface
        self.tcp_backlog = tcp_backlog
        self.tls_key = tls_key
        self.tls_certificate = tls_certificate
        self.tls_chain_certificates = tls_chain_certificates
        self.tls_ca_certificates = tls_ca_certificates
        self.tls_dhparam = tls_dhparam
        self.tls_ciphers = tls_ciphers
        self.http_client_timeout = http_client_timeout
        self.http_hsts = http_hsts
        self.http_hsts_max_age = http_hsts_max_age
        self.http_access_log = http_access_log
        self.http_display_tracebacks = http_display_tracebacks

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if not Cluster.__eq__(self, other):
            return False
        if other.tcp_version != self.tcp_version:
            return False
        if other.tcp_port != self.tcp_port:
            return False
        if other.tcp_shared != self.tcp_shared:
            return False
        if other.tcp_interface != self.tcp_interface:
            return False
        if other.tcp_backlog != self.tcp_backlog:
            return False
        if other.tls_key != self.tls_key:
            return False
        if other.tls_certificate != self.tls_certificate:
            return False
        if other.tls_chain_certificates != self.tls_chain_certificates:
            return False
        if other.tls_ca_certificates != self.tls_ca_certificates:
            return False
        if other.tls_dhparam != self.tls_dhparam:
            return False
        if other.tls_ciphers != self.tls_ciphers:
            return False
        if other.http_client_timeout != self.http_client_timeout:
            return False
        if other.http_hsts != self.http_hsts:
            return False
        if other.http_hsts_max_age != self.http_hsts_max_age:
            return False
        if other.http_access_log != self.http_access_log:
            return False
        if other.http_display_tracebacks != self.http_display_tracebacks:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return pprint.pformat(self.marshal())

    def marshal(self):
        """
        Marshal this object to a generic host language object.

        :return: dict
        """
        obj = Cluster.marshal(self)

        obj.update({
            'tcp_version': self.tcp_version,
            'tcp_port': self.tcp_port,
            'tcp_shared': self.tcp_shared,
            'tcp_interface': self.tcp_interface,
            'tcp_backlog': self.tcp_backlog,
            'tls_key': self.tls_key,
            'tls_certificate': self.tls_certificate,
            'tls_chain_certificates': self.tls_chain_certificates,
            'tls_ca_certificates': self.tls_ca_certificates,
            'tls_dhparam': self.tls_dhparam,
            'tls_ciphers': self.tls_ciphers,
            'http_client_timeout': self.http_client_timeout,
            'http_hsts': self.http_hsts,
            'http_hsts_max_age': self.http_hsts_max_age,
            'http_access_log': self.http_access_log,
            'http_display_tracebacks': self.http_display_tracebacks,
        })

        return obj

    @staticmethod
    def parse(data):
        """
        Parse generic host language object into an object of this class.

        :param data: Generic host language object
        :type data: dict

        :return: instance of :class:`ManagementRealm`
        """
        assert type(data) == dict

        obj = Cluster.parse(data)
        data = obj._unknown or {}

        # future attributes (yet unknown) are not only ignored, but passed through!
        _unknown = {}
        for k in data:
            if k not in [
                    'tcp_version', 'tcp_port', 'tcp_shared', 'tcp_interface', 'tcp_backlog', 'tls_key',
                    'tls_certificate', 'tls_chain_certificates', 'tls_ca_certificates', 'tls_dhparam',
                    'tls_ciphers', 'http_client_timeout', 'http_hsts', 'http_hsts_max_age', 'http_access_log',
                    'http_display_tracebacks'
            ]:
                _unknown[k] = data[k]

        tcp_version = data.get('tcp_version', None)
        assert tcp_version is None or (type(tcp_version) == int)

        tcp_port = data.get('tcp_port', None)
        assert tcp_port is None or (type(tcp_port) == int)

        tcp_shared = data.get('tcp_shared', None)
        assert tcp_shared is None or (type(tcp_shared) == bool)

        tcp_interface = data.get('tcp_interface', None)
        assert tcp_interface is None or (type(tcp_interface) == str)

        tcp_backlog = data.get('tcp_backlog', None)
        assert tcp_backlog is None or (type(tcp_backlog) == int)

        tls_key = data.get('tls_key', None)
        assert tls_key is None or (type(tls_key) == str)

        tls_certificate = data.get('tls_certificate', None)
        assert tls_certificate is None or (type(tls_certificate) == str)

        tls_chain_certificates = data.get('tls_chain_certificates', None)
        assert tls_chain_certificates is None or (type(tls_chain_certificates) == list)

        tls_ca_certificates = data.get('tls_ca_certificates', None)
        assert tls_ca_certificates is None or (type(tls_ca_certificates) == list)

        tls_dhparam = data.get('tls_dhparam', None)
        assert tls_dhparam is None or (type(tls_dhparam) == str)

        tls_ciphers = data.get('tls_ciphers', None)
        assert tls_ciphers is None or (type(tls_ciphers) == str)

        http_client_timeout = data.get('http_client_timeout', None)
        assert http_client_timeout is None or (type(http_client_timeout) == int)

        http_hsts = data.get('http_hsts', None)
        assert http_hsts is None or (type(http_hsts) == bool)

        http_hsts_max_age = data.get('http_hsts_max_age', None)
        assert http_hsts_max_age is None or (type(http_hsts_max_age) == int)

        http_access_log = data.get('http_access_log', None)
        assert http_access_log is None or (type(http_access_log) == bool)

        http_display_tracebacks = data.get('http_display_tracebacks', None)
        assert http_display_tracebacks is None or (type(http_display_tracebacks) == bool)

        obj = WebCluster(oid=obj.oid,
                         label=obj.label,
                         description=obj.description,
                         tags=obj.tags,
                         name=obj.name,
                         status=obj.status,
                         owner_oid=obj.owner_oid,
                         changed=obj.changed,
                         tcp_version=tcp_version,
                         tcp_port=tcp_port,
                         tcp_shared=tcp_shared,
                         tcp_interface=tcp_interface,
                         tcp_backlog=tcp_backlog,
                         tls_key=tls_key,
                         tls_certificate=tls_certificate,
                         tls_chain_certificates=tls_chain_certificates,
                         tls_ca_certificates=tls_ca_certificates,
                         tls_dhparam=tls_dhparam,
                         tls_ciphers=tls_ciphers,
                         http_client_timeout=http_client_timeout,
                         http_hsts=http_hsts,
                         http_hsts_max_age=http_hsts_max_age,
                         http_access_log=http_access_log,
                         http_display_tracebacks=http_display_tracebacks,
                         _unknown=_unknown)

        return obj
