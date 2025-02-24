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


class WebClusterNodeMembership(ClusterNodeMembership):
    """
    Information about memberships of nodes in web clusters.
    """
    def __init__(self,
                 cluster_oid: Optional[UUID] = None,
                 node_oid: Optional[UUID] = None,
                 parallel: Optional[int] = None,
                 standby: Optional[bool] = None,
                 _unknown=None):
        """

        :param cluster_oid: Object ID of the cluster the node is member in.

        :param node_oid: Object ID of the node that is member in the cluster.

        :param parallel: Default parallel degree per node in this cluster.

        :param standby: Flag indicating whether this is a (currently inactive) standby node.
        """
        ClusterNodeMembership.__init__(self, cluster_oid=cluster_oid, node_oid=node_oid, _unknown=_unknown)
        self.parallel = parallel
        self.standby = standby

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if not ClusterNodeMembership.__eq__(self, other):
            return False
        if other.parallel != self.parallel:
            return False
        if other.standby != self.standby:
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
            'parallel': self.parallel,
            'standby': self.standby,
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
            if k not in ['parallel', 'standby']:
                _unknown[k] = data[k]

        parallel = None
        if 'parallel' in data and data['parallel']:
            assert type(data['parallel']) == int
            parallel = data['parallel']

        standby = None
        if 'standby' in data and data['standby']:
            assert data['standby'] is None or type(data['standby']) == bool
            standby = data['standby']

        obj = WebClusterNodeMembership(cluster_oid=obj.cluster_oid,
                                       node_oid=obj.node_oid,
                                       parallel=parallel,
                                       standby=standby,
                                       _unknown=_unknown)

        return obj
