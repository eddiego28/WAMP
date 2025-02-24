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


class Role(ConfigurationElement):
    """
    Roles created for use with application-level authorization and permissions
    in application realms.
    """
    def __init__(self,
                 oid: Optional[UUID] = None,
                 label: Optional[str] = None,
                 description: Optional[str] = None,
                 tags: Optional[List[str]] = None,
                 name: Optional[str] = None,
                 created: Optional[np.datetime64] = None,
                 owner: Optional[UUID] = None,
                 _unknown=None):
        """

        :param oid: Object ID of role

        :param label: Optional user label of role

        :param description: Optional user description of role

        :param tags: Optional list of user tags on role

        :param name: Name of role

        :param created: Timestamp when the role was created

        :param owner: Owning user (object ID)
        """
        ConfigurationElement.__init__(self, oid=oid, label=label, description=description, tags=tags)
        self.name = name
        self.created = created
        self.owner = owner

        # private member with unknown/untouched data passing through
        self._unknown = _unknown

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if not ConfigurationElement.__eq__(self, other):
            return False
        if other.name != self.name:
            return False
        if other.created != self.created:
            return False
        if other.owner != self.owner:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return pprint.pformat(self.marshal())

    def copy(self, other, overwrite=False):
        """
        Copy over other object.

        :param other: Other role to copy data from.
        :type other: instance of :class:`ManagementRealm`
        :return:
        """
        ConfigurationElement.copy(self, other, overwrite=overwrite)

        if (not self.name and other.name) or overwrite:
            self.name = other.name
        if (not self.created and other.created) or overwrite:
            self.created = other.created
        if (not self.owner and other.owner) or overwrite:
            self.owner = other.owner

        # _unknown is not copied!

    def marshal(self):
        """
        Marshal this object to a generic host language object.

        :return: dict
        """
        obj = ConfigurationElement.marshal(self)

        obj.update({
            'oid': str(self.oid) if self.oid else None,
            'name': self.name,
            'created': int(self.created) if self.created else None,
            'owner': str(self.owner) if self.owner else None,
        })

        if self._unknown:
            # pass through all attributes unknown
            obj.update(self._unknown)

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
            if k not in ['oid', 'name', 'owner', 'created']:
                _unknown[k] = data[k]

        name = data.get('name', None)
        assert name is None or type(name) == str

        owner = data.get('owner', None)
        assert owner is None or type(owner) == str
        if owner:
            owner = UUID(owner)

        created = data.get('created', None)
        assert created is None or type(created) == int
        if created:
            created = np.datetime64(created, 'ns')

        obj = Role(oid=obj.oid,
                   label=obj.label,
                   description=obj.description,
                   tags=obj.tags,
                   name=name,
                   owner=owner,
                   created=created,
                   _unknown=_unknown)

        return obj
