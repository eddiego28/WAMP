##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################

import uuid
import pprint
from typing import Optional

import numpy as np

from cfxdb.mrealm.types import STATUS_BY_CODE, STATUS_BY_NAME


class RouterWorkerGroupClusterPlacement(object):
    """
    Placement of router worker groups onto router clusters, specifically **router workers**
    and **xbrmm workers** running as part of router worker groups.
    """
    def __init__(self,
                 oid: Optional[uuid.UUID] = None,
                 worker_group_oid: Optional[uuid.UUID] = None,
                 cluster_oid: Optional[uuid.UUID] = None,
                 node_oid: Optional[uuid.UUID] = None,
                 worker_name: Optional[str] = None,
                 status: Optional[int] = None,
                 changed: Optional[np.datetime64] = None,
                 tcp_listening_port: Optional[int] = None,
                 _unknown: Optional[dict] = None):
        """

        :param oid: Object ID of this placement itself.

        :param worker_group_oid: Object ID of the router worker group this placement applies to.
            Refers to :class:`cfxdb.mrealm.RouterWorkerGroup`

        :param cluster_oid: Object ID of the router cluster this placement applies to.
            Refers to :class:`cfxdb.mrealm.RouterCluster`

        :param node_oid: Object ID of the node (within the router cluster) this placement is assigned to.
            Refers to :class:`cfxdb.mrealm.Node`

        :param worker_name: Run-time ID (in the node) of the router worker this placement is assigned to.

        :param status: Status of this placement, which essentially reflects the router worker status of this placement.

        :param changed: Timestamp when the status of this placement last changed.

        :param tcp_listening_port: TCP listening port the router worker this placement is assigned to is listening on
            for incoming proxy front-end and router-to-router connections.
        """
        self.oid = oid
        self.worker_group_oid = worker_group_oid
        self.cluster_oid = cluster_oid
        self.node_oid = node_oid
        self.worker_name = worker_name
        self.status = status
        self.changed = changed
        self.tcp_listening_port = tcp_listening_port
        self._unknown = _unknown

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if other.oid != self.oid:
            return False
        if other.worker_group_oid != self.worker_group_oid:
            return False
        if other.cluster_oid != self.cluster_oid:
            return False
        if other.node_oid != self.node_oid:
            return False
        if other.worker_name != self.worker_name:
            return False
        if other.status != self.status:
            return False
        if other.changed != self.changed:
            return False
        if other.tcp_listening_port != self.tcp_listening_port:
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
            'oid': str(self.oid) if self.oid else None,
            'worker_group_oid': str(self.worker_group_oid),
            'cluster_oid': str(self.cluster_oid),
            'node_oid': str(self.node_oid),
            'worker_name': self.worker_name,
            'status': STATUS_BY_CODE[self.status] if self.status else None,
            'changed': int(self.changed) if self.changed else None,
            'tcp_listening_port': self.tcp_listening_port,
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
            if k not in [
                    'oid', 'worker_group_oid', 'cluster_oid', 'node_oid', 'worker_name', 'status', 'changed',
                    'tcp_listening_port'
            ]:
                _unknown[k] = data[k]

        oid = None
        if 'oid' in data:
            assert type(data['oid']) == str
            oid = uuid.UUID(data['oid'])

        worker_group_oid = None
        if 'worker_group_oid' in data:
            assert type(data['worker_group_oid']) == str
            worker_group_oid = uuid.UUID(data['worker_group_oid'])

        cluster_oid = None
        if 'cluster_oid' in data:
            assert type(data['cluster_oid']) == str
            cluster_oid = uuid.UUID(data['cluster_oid'])

        node_oid = None
        if 'node_oid' in data:
            assert type(data['node_oid']) == str
            node_oid = uuid.UUID(data['node_oid'])

        worker_name = None
        if 'worker_name' in data:
            assert type(data['worker_name']) == str
            worker_name = data['worker_name']

        status = data.get('status', None)
        assert status is None or (type(status) == str)
        status = STATUS_BY_NAME.get(status, None)

        changed = data.get('changed', None)
        assert changed is None or (type(changed) == int)
        if changed:
            changed = np.datetime64(changed, 'ns')

        tcp_listening_port = data.get('tcp_listening_port', None)
        assert tcp_listening_port is None or (type(tcp_listening_port) == int
                                              and 0 <= tcp_listening_port < 65536)

        obj = RouterWorkerGroupClusterPlacement(oid=oid,
                                                worker_group_oid=worker_group_oid,
                                                cluster_oid=cluster_oid,
                                                worker_name=worker_name,
                                                node_oid=node_oid,
                                                status=status,
                                                changed=changed,
                                                tcp_listening_port=tcp_listening_port,
                                                _unknown=_unknown)

        return obj
