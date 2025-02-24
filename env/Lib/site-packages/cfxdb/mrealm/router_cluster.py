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


class RouterCluster(Cluster):
    """
    A router cluster is able to run (application) realms, and is hosted on a groups of router workers
    kept in sync and meshed via router-to-router links.
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

        :param oid: Object ID of this router cluster.

        :param label: Optional user label of this router cluster.

        :param description: Optional user description of this router cluster.

        :param tags: Optional list of user tags on this router cluster.
        """
        Cluster.__init__(self,
                         oid=oid,
                         label=label,
                         description=description,
                         tags=tags,
                         name=name,
                         status=status,
                         owner_oid=owner_oid,
                         changed=changed)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if not Cluster.__eq__(self, other):
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return '\n{}\n'.format(pprint.pformat(self.marshal()))

    def marshal(self):
        """
        Marshal this object to a generic host language object.

        :return: dict
        """
        obj = Cluster.marshal(self)
        obj.update({})
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
        data = obj._unknown

        # future attributes (yet unknown) are not only ignored, but passed through!
        _unknown = {}
        for k in data:
            if k not in []:
                _unknown[k] = data[k]

        obj = RouterCluster(oid=obj.oid,
                            label=obj.label,
                            description=obj.description,
                            tags=obj.tags,
                            name=obj.name,
                            status=obj.status,
                            owner_oid=obj.owner_oid,
                            changed=obj.changed,
                            _unknown=_unknown)

        return obj
