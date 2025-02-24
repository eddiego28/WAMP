##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################

from typing import Optional
import pprint
from uuid import UUID


class ClusterNodeMembership(object):
    """
    Membership of a node in a cluster.
    """
    def __init__(self, cluster_oid: Optional[UUID] = None, node_oid: Optional[UUID] = None, _unknown=None):
        """

        :param cluster_oid: Object ID of the cluster the node is member in.

        :param node_oid: Object ID of the node that is member in the cluster.
        """
        self.cluster_oid = cluster_oid
        self.node_oid = node_oid
        self._unknown = _unknown

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if other.cluster_oid != self.cluster_oid:
            return False
        if other.node_oid != self.node_oid:
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
        obj = {
            'cluster_oid': str(self.cluster_oid),
            'node_oid': str(self.node_oid),
        }
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

        # future attributes (yet unknown) are not only ignored, but passed through!
        _unknown = {}
        for k in data:
            if k not in ['cluster_oid', 'node_oid']:
                _unknown[k] = data[k]

        cluster_oid = None
        if 'cluster_oid' in data:
            assert type(data['cluster_oid']) == str
            cluster_oid = UUID(data['cluster_oid'])

        node_oid = None
        if 'node_oid' in data:
            assert type(data['node_oid']) == str
            node_oid = UUID(data['node_oid'])

        obj = ClusterNodeMembership(cluster_oid=cluster_oid, node_oid=node_oid, _unknown=_unknown)

        return obj
