##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################

import pprint
from uuid import UUID
from typing import Optional, List

from cfxdb.common import ConfigurationElement


class Node(ConfigurationElement):
    """
    Nodes paired with management realms on this master node.
    """
    def __init__(self,
                 oid: Optional[UUID] = None,
                 label: Optional[str] = None,
                 description: Optional[str] = None,
                 tags: Optional[List[str]] = None,
                 owner_oid: Optional[UUID] = None,
                 pubkey: Optional[str] = None,
                 cluster_ip: Optional[str] = None,
                 mrealm_oid: Optional[UUID] = None,
                 authid: Optional[str] = None,
                 authextra: Optional[dict] = None,
                 _unknown=None):
        """

        :param oid: Object ID of node

        :param label: Optional user label of node

        :param description: Optional user description of node

        :param tags: Optional list of user tags on node

        :param owner_oid: Object owner.

        :param pubkey: The WAMP-cryptosign node public key (32 bytes as HEX encoded string).

        :param cluster_ip: The (private) clustering IP for incoming rlinks to connect to.

        :param mrealm_oid: The management realm the node will be joined on.

        :param authid: The WAMP ``authid`` the node will be authenticated as.

        :param authextra: Optional ``authextra`` the node will be sent to when authenticating.

        :param _unknown: Any unparsed/unprocessed data attributes
        """
        ConfigurationElement.__init__(self, oid=oid, label=label, description=description, tags=tags)
        self.owner_oid = owner_oid
        self.pubkey = pubkey
        self.cluster_ip = cluster_ip
        self.mrealm_oid = mrealm_oid
        self.authid = authid
        self.authextra = authextra

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if not ConfigurationElement.__eq__(self, other):
            return False
        if other.owner_oid != self.owner_oid:
            return False
        if other.pubkey != self.pubkey:
            return False
        if other.cluster_ip != self.cluster_ip:
            return False
        if other.mrealm_oid != self.mrealm_oid:
            return False
        if other.authid != self.authid:
            return False
        if other.authextra != self.authextra:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return '\n{}\n'.format(pprint.pformat(self.marshal()))

    def copy(self, other, overwrite=False):
        """
        Copy over other object.

        :param other: Other management realm to copy data from.
        :type other: instance of :class:`ManagementRealm`
        :return:
        """
        ConfigurationElement.copy(self, other, overwrite=overwrite)

        if (not self.owner_oid and other.owner_oid) or overwrite:
            self.owner_oid = other.owner_oid
        if (not self.pubkey and other.pubkey) or overwrite:
            self.pubkey = other.pubkey
        if (not self.cluster_ip and other.cluster_ip) or overwrite:
            self.cluster_ip = other.cluster_ip
        if (not self.mrealm_oid and other.mrealm_oid) or overwrite:
            self.mrealm_oid = other.mrealm_oid
        if (not self.authid and other.authid) or overwrite:
            self.authid = other.authid
        if (not self.authextra and other.authextra) or overwrite:
            self.authextra = other.authextra

        # _unknown is not copied!

    def marshal(self):
        """
        Marshal this object to a generic host language object.

        :return: dict
        """
        obj = ConfigurationElement.marshal(self)

        obj.update({
            'owner_oid': str(self.owner_oid) if self.owner_oid else None,
            'pubkey': self.pubkey,
            'cluster_ip': self.cluster_ip,
            'mrealm_oid': str(self.mrealm_oid) if self.mrealm_oid else None,
            'authid': self.authid,
            'authextra': self.authextra,
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

        obj = ConfigurationElement.parse(data)
        data = obj._unknown

        # future attributes (yet unknown) are not only ignored, but passed through!
        _unknown = {}
        for k in data:
            if k not in ['owner_oid', 'pubkey', 'cluster_ip', 'mrealm_oid', 'authid', 'authextra']:
                _unknown[k] = data[k]

        owner_oid = data.get('owner_oid', None)
        assert owner_oid is None or type(owner_oid) == str
        if owner_oid:
            owner_oid = UUID(owner_oid)

        pubkey = data.get('pubkey', None)
        assert pubkey is None or (type(pubkey) == str and len(pubkey) == 64)

        cluster_ip = data.get('cluster_ip', None)
        assert cluster_ip is None or type(cluster_ip)

        mrealm_oid = data.get('mrealm_oid', None)
        assert mrealm_oid is None or type(mrealm_oid) == str
        if mrealm_oid:
            mrealm_oid = UUID(mrealm_oid)

        authid = data.get('authid', None)
        assert authid is None or type(authid) == str

        authextra = data.get('authextra', None)
        assert authextra is None or type(authextra) == dict

        obj = Node(oid=obj.oid,
                   label=obj.label,
                   description=obj.description,
                   tags=obj.tags,
                   owner_oid=owner_oid,
                   pubkey=pubkey,
                   cluster_ip=cluster_ip,
                   mrealm_oid=mrealm_oid,
                   authid=authid,
                   authextra=authextra,
                   _unknown=_unknown)

        return obj
