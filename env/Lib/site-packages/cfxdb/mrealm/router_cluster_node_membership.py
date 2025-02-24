##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################

from typing import Optional
import pprint
from uuid import UUID

from cfxdb.mrealm.cluster_node_membership import ClusterNodeMembership


class RouterClusterNodeMembership(ClusterNodeMembership):
    """
    Membership of a managed node (paired within a management realm) to a router cluster.
    A router cluster is able to run "data planes", which are groups of router workers kept in sync,
    and meshed via router-to-router links. Finally, "(application) realms" can be started in data planes.
    """
    def __init__(self,
                 cluster_oid: Optional[UUID] = None,
                 node_oid: Optional[UUID] = None,
                 softlimit: Optional[int] = None,
                 hardlimit: Optional[int] = None,
                 _unknown=None):
        """

        :param cluster_oid: Object ID of router cluster the node is becoming member of.

        :param node_oid: Object ID of the node becoming member of the router cluster.

        :param softlimit: Limits the number of router workers started on this node. When this number of workers
            is reached, efforts are taken to actively reduce the resource load on this node (eg stopping
            other running router workers "currently being idle"). New router workers will still be started.

        :param hardlimit: Maximum number of router workers started on this node. This hard limits the
            number of router workers started on this node.
        """
        ClusterNodeMembership.__init__(self, cluster_oid=cluster_oid, node_oid=node_oid, _unknown=_unknown)
        self.softlimit = softlimit
        self.hardlimit = hardlimit

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if not ClusterNodeMembership.__eq__(self, other):
            return False
        if other.softlimit != self.softlimit:
            return False
        if other.hardlimit != self.hardlimit:
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
        obj = ClusterNodeMembership.marshal(self)
        obj.update({
            'softlimit': self.softlimit,
            'hardlimit': self.hardlimit,
        })
        return obj

    @staticmethod
    def parse(data):
        """
        Parse generic host language object into an object of this class.

        :param data: Generic host language object
        :type data: dict

        :return: instance of :class:`WebService`
        """
        assert type(data) == dict

        obj = ClusterNodeMembership.parse(data)
        data = obj._unknown or {}

        # future attributes (yet unknown) are not only ignored, but passed through!
        _unknown = {}
        for k in data:
            if k not in ['softlimit', 'hardlimit']:
                _unknown[k] = data[k]

        softlimit = None
        if 'softlimit' in data and data['softlimit']:
            assert type(data['softlimit']) == int
            softlimit = data['softlimit']

        hardlimit = None
        if 'hardlimit' in data and data['hardlimit']:
            assert type(data['hardlimit']) == int
            hardlimit = data['hardlimit']

        obj = RouterClusterNodeMembership(cluster_oid=obj.cluster_oid,
                                          node_oid=obj.node_oid,
                                          softlimit=softlimit,
                                          hardlimit=hardlimit,
                                          _unknown=_unknown)

        return obj
