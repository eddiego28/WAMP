##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################

from typing import Optional
import pprint
from uuid import UUID


class ApplicationRealmRoleAssociation(object):
    """
    Association of a role with an application realm.
    """
    def __init__(self, arealm_oid: Optional[UUID] = None, role_oid: Optional[UUID] = None, _unknown=None):
        self.arealm_oid = arealm_oid
        self.role_oid = role_oid
        self._unknown = _unknown
        """

        :param arealm_oid: Object ID of the application realm this association applies to.

        :param role_oid: Object ID of the role this association applies to.
        """

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if other.arealm_oid != self.arealm_oid:
            return False
        if other.role_oid != self.role_oid:
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
            'arealm_oid': str(self.arealm_oid),
            'role_oid': str(self.role_oid),
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
            if k not in ['arealm_oid', 'role_oid']:
                _unknown[k] = data[k]

        arealm_oid = None
        if 'arealm_oid' in data:
            assert type(data['arealm_oid']) == str
            arealm_oid = UUID(data['arealm_oid'])

        role_oid = None
        if 'role_oid' in data:
            assert type(data['role_oid']) == str
            role_oid = UUID(data['role_oid'])

        obj = ApplicationRealmRoleAssociation(arealm_oid=arealm_oid, role_oid=role_oid, _unknown=_unknown)

        return obj
