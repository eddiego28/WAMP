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
from cfxdb.mrealm.types import STATUS_BY_CODE, STATUS_BY_NAME


class RouterWorkerGroup(ConfigurationElement):
    """
    Router worker group database configuration object.
    """
    def __init__(self,
                 oid: Optional[UUID] = None,
                 label: Optional[str] = None,
                 description: Optional[str] = None,
                 tags: Optional[List[str]] = None,
                 cluster_oid: Optional[UUID] = None,
                 name: Optional[str] = None,
                 scale: Optional[int] = None,
                 status: Optional[int] = None,
                 changed: Optional[np.datetime64] = None,
                 _unknown=None):
        """

        :param oid: Object ID of router worker group.

        :param label: Optional user label of router worker group.

        :param description: Optional user description of router worker group.

        :param tags: Optional list of user tags on router worker group.
        """
        ConfigurationElement.__init__(self,
                                      oid=oid,
                                      label=label,
                                      description=description,
                                      tags=tags,
                                      _unknown=_unknown)
        self.cluster_oid = cluster_oid
        self.name = name
        self.scale = scale or 1
        self.status = status
        self.changed = changed

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if not ConfigurationElement.__eq__(self, other):
            return False
        if other.cluster_oid != self.cluster_oid:
            return False
        if other.name != self.name:
            return False
        if other.scale != self.scale:
            return False
        if other.status != self.status:
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
            'cluster_oid': str(self.cluster_oid) if self.cluster_oid else None,
            'name': self.name,
            'scale': self.scale,
            'status': STATUS_BY_CODE[self.status] if self.status else None,
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
            if k not in ['cluster_oid', 'name', 'scale', 'status', 'changed']:
                _unknown[k] = data[k]

        cluster_oid = data.get('cluster_oid', None)
        assert cluster_oid is None or (type(cluster_oid) == str)
        cluster_oid = UUID(cluster_oid)

        name = data.get('name', None)
        assert name is None or (type(name) == str)

        scale = data.get('scale', 1)
        assert scale is None or (type(scale) == int and scale >= 1 and scale <= 128
                                 ), 'scale must be an integer from 1 to 128, but was {}'.format(scale)

        status = data.get('status', None)
        assert status is None or (type(status) == str)
        status = STATUS_BY_NAME.get(status, None)

        changed = data.get('changed', None)
        assert changed is None or (type(changed) == int)
        if changed:
            changed = np.datetime64(changed, 'ns')

        obj = RouterWorkerGroup(oid=obj.oid,
                                label=obj.label,
                                description=obj.description,
                                tags=obj.tags,
                                cluster_oid=cluster_oid,
                                name=name,
                                scale=scale,
                                status=status,
                                changed=changed,
                                _unknown=_unknown)

        return obj
