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

from cfxdb.common import ConfigurationElement
from cfxdb.gen.mrealm.ClusterStatus import ClusterStatus

STATUS_BY_CODE = {
    ClusterStatus.NONE: 'NONE',
    ClusterStatus.STOPPED: 'STOPPED',
    ClusterStatus.STARTING: 'STARTING',
    ClusterStatus.RUNNING: 'RUNNING',
    ClusterStatus.PAUSED: 'PAUSED',
    ClusterStatus.STOPPING: 'STOPPING',
    ClusterStatus.ERROR: 'ERROR',
    ClusterStatus.DEGRADED: 'DEGRADED',
}

STATUS_BY_NAME = {
    'NONE': ClusterStatus.NONE,
    'STOPPED': ClusterStatus.STOPPED,
    'STARTING': ClusterStatus.STARTING,
    'RUNNING': ClusterStatus.RUNNING,
    'PAUSED': ClusterStatus.PAUSED,
    'STOPPING': ClusterStatus.STOPPING,
    'ERROR': ClusterStatus.ERROR,
    'DEGRADED': ClusterStatus.DEGRADED,
}

STATUS_STOPPED = ClusterStatus.STOPPED
STATUS_STARTING = ClusterStatus.STARTING
STATUS_RUNNING = ClusterStatus.RUNNING
STATUS_PAUSED = ClusterStatus.PAUSED
STATUS_STOPPING = ClusterStatus.STOPPING
STATUS_ERROR = ClusterStatus.ERROR
STATUS_DEGRADED = ClusterStatus.DEGRADED


class Cluster(ConfigurationElement):
    """
    CFC Cluster database configuration object.
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
                 _unknown=None):
        """

        :param oid: Object ID of this cluster

        :param label: Optional user label of this cluster

        :param description: Optional user description of this cluster

        :param tags: Optional list of user tags on this cluster
        """
        ConfigurationElement.__init__(self,
                                      oid=oid,
                                      label=label,
                                      description=description,
                                      tags=tags,
                                      _unknown=_unknown)
        self.name = name
        self.status = status
        self.owner_oid = owner_oid
        self.changed = changed

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if not ConfigurationElement.__eq__(self, other):
            return False
        if other.name != self.name:
            return False
        if other.status != self.status:
            return False
        if other.owner_oid != self.owner_oid:
            return False
        if other.changed != self.changed:
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
        obj = ConfigurationElement.marshal(self)

        obj.update({
            'name': self.name,
            'status': STATUS_BY_CODE[self.status] if self.status else None,
            'owner_oid': str(self.owner_oid) if self.owner_oid else None,
            'changed': int(self.changed) if self.changed else None,
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
        data = obj._unknown or {}

        # future attributes (yet unknown) are not only ignored, but passed through!
        _unknown = dict()
        for k in data:
            if k not in ['name', 'status', 'owner_oid', 'changed']:
                _unknown[k] = data[k]

        name = data.get('name', None)
        assert name is None or (type(name) == str)

        status = data.get('status', None)
        assert status is None or (type(status) == str)
        status = STATUS_BY_NAME.get(status, None)

        owner_oid = data.get('owner_oid', None)
        assert owner_oid is None or (type(owner_oid) == str)
        if owner_oid:
            owner_oid = UUID(owner_oid)

        changed = data.get('changed', None)
        assert changed is None or (type(changed) == int)
        if changed:
            changed = np.datetime64(changed, 'ns')

        obj = Cluster(oid=obj.oid,
                      label=obj.label,
                      description=obj.description,
                      tags=obj.tags,
                      name=name,
                      status=status,
                      owner_oid=owner_oid,
                      changed=changed,
                      _unknown=_unknown)

        return obj
