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


class Principal(ConfigurationElement):
    """
    Principals created for use with WAMP authentication. A principal represents the identity
    an application client is authenticated to the application realm joined.

    A principal must have at least one :class:`cfxdb.mrealmschema.Credential` added.
    When an application client connects, it will offer an ``authmethod`` and request a ``realm``
    and (usually) ``authid``. When a matching :class:`cfxdb.mrealmschema.Credential` is found,
    and authentication succeeds using that, the client will be authenticated under the
    :class:`cfxdb.mrealmschema.Principal` associated with the credential.

    .. note::

        It is important to note that while the ``realm`` and ``authid`` requested by the client
        (and defined in the respective :class:`cfxdb.mrealmschema.Credential`) will *usually* be identical
        to the ``realm`` and ``authid`` actually assigned (as defined in the :class:`cfxdb.mrealmschema.Principal`
        associated with the credential), this is allowed to differ in *general*.
    """
    def __init__(self,
                 oid: Optional[UUID] = None,
                 label: Optional[str] = None,
                 description: Optional[str] = None,
                 tags: Optional[List[str]] = None,
                 modified: Optional[int] = None,
                 arealm_oid: Optional[UUID] = None,
                 authid: Optional[str] = None,
                 role_oid: Optional[UUID] = None,
                 authextra: Optional[dict] = None,
                 _unknown=None):
        """

        :param oid: Object ID of principal

        :param label: Optional user label of principal

        :param description: Optional user description of principal

        :param tags: Optional list of user tags on principal

        :param modified: Timestamp when the principal was last modified

        :param arealm_oid: ID of the application realm the authenticated principal will be joined to.

        :param authid: WAMP authid of the principal, must be unique within the application realm at any moment in time.

        :param role_oid: ID of the role the authenticated principal will be joined to the application realm.

        :param authextra: Optional authextra information returned to the authenticating principal.
        """
        ConfigurationElement.__init__(self, oid=oid, label=label, description=description, tags=tags)
        self.modified = modified
        self.arealm_oid = arealm_oid
        self.authid = authid
        self.role_oid = role_oid
        self.authextra = authextra

        # private member with unknown/untouched data passing through
        self._unknown = _unknown

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if not ConfigurationElement.__eq__(self, other):
            return False
        if other.modified != self.modified:
            return False
        if other.arealm_oid != self.arealm_oid:
            return False
        if other.authid != self.authid:
            return False
        if other.role_oid != self.role_oid:
            return False
        if other.authextra != self.authextra:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return pprint.pformat(self.marshal())

    def copy(self, other, overwrite=False):
        """
        Copy over other object.

        :param other: Other principal to copy data from.
        :type other: instance of :class:`cfxdb.mrealm.Principal`
        :return:
        """
        ConfigurationElement.copy(self, other, overwrite=overwrite)

        if (not self.modified and other.modified) or overwrite:
            self.modified = other.modified
        if (not self.arealm_oid and other.arealm_oid) or overwrite:
            self.arealm_oid = other.arealm_oid
        if (not self.authid and other.authid) or overwrite:
            self.authid = other.authid
        if (not self.role_oid and other.role_oid) or overwrite:
            self.role_oid = other.role_oid
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
            'oid': str(self.oid) if self.oid else None,
            'modified': int(self.modified) if self.modified else None,
            'arealm_oid': str(self.arealm_oid) if self.arealm_oid else None,
            'authid': self.authid,
            'role_oid': str(self.role_oid) if self.role_oid else None,
            'authextra': self.authextra,
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
            if k not in ['oid', 'modified', 'arealm_oid', 'authid', 'role_oid', 'authextra']:
                _unknown[k] = data[k]

        modified = data.get('modified', None)
        assert modified is None or type(modified) == int
        if modified:
            modified = np.datetime64(modified, 'ns')

        arealm_oid = data.get('arealm_oid', None)
        assert arealm_oid is None or type(arealm_oid) == str
        if arealm_oid:
            arealm_oid = UUID(arealm_oid)

        authid = data.get('authid', None)
        assert authid is None or type(authid) == str

        role_oid = data.get('role_oid', None)
        assert role_oid is None or type(role_oid) == str
        if role_oid:
            role_oid = UUID(role_oid)

        authextra = data.get('authextra', None)
        assert authextra is None or type(authextra) == dict

        obj = Principal(oid=obj.oid,
                        label=obj.label,
                        description=obj.description,
                        tags=obj.tags,
                        modified=modified,
                        arealm_oid=arealm_oid,
                        authid=authid,
                        role_oid=role_oid,
                        authextra=authextra,
                        _unknown=_unknown)

        return obj
