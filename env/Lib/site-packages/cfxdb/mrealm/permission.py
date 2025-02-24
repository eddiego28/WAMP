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


class Permission(ConfigurationElement):
    """
    Role permission database object.
    """
    MATCH_TYPE_NONE: int = 0
    MATCH_TYPE_EXACT: int = 1
    MATCH_TYPE_PREFIX: int = 2
    MATCH_TYPE_WILDCARD: int = 3
    MATCH_TYPES_TOSTR = {
        0: None,
        1: 'exact',
        2: 'prefix',
        3: 'wildcard',
    }
    MATCH_TYPES_FROMSTR = {val: key for key, val in MATCH_TYPES_TOSTR.items()}

    URI_CHECK_LEVEL_NONE: int = 0
    URI_CHECK_LEVEL_STRICT: int = 1
    URI_CHECK_LEVEL_LOOSE: int = 2
    URI_CHECK_LEVELS_TOSTR = {0: None, 1: 'strict', 2: 'loose'}
    URI_CHECK_LEVELS_FROMSTR = {val: key for key, val in URI_CHECK_LEVELS_TOSTR.items()}

    def __init__(self,
                 oid: Optional[UUID] = None,
                 label: Optional[str] = None,
                 description: Optional[str] = None,
                 tags: Optional[List[str]] = None,
                 role_oid: Optional[UUID] = None,
                 uri: Optional[str] = None,
                 uri_check_level: Optional[int] = None,
                 match: Optional[int] = None,
                 allow_call: Optional[bool] = None,
                 allow_register: Optional[bool] = None,
                 allow_publish: Optional[bool] = None,
                 allow_subscribe: Optional[bool] = None,
                 disclose_caller: Optional[bool] = None,
                 disclose_publisher: Optional[bool] = None,
                 cache: Optional[bool] = None,
                 created: Optional[np.datetime64] = None,
                 owner: Optional[UUID] = None,
                 _unknown=None):
        """

        :param oid: Object ID of this permission object

        :param label: Optional user label of permission

        :param description: Optional user description of permission

        :param tags: Optional list of user tags on permission

        :param role_oid: Object ID of role this permission applies to.

        :param uri: URI matched for permission.

        :param created: Timestamp when the permission was created

        :param owner: Owning user (object ID)
        """
        ConfigurationElement.__init__(self, oid=oid, label=label, description=description, tags=tags)
        self.role_oid = role_oid
        self.uri = uri
        self.uri_check_level = uri_check_level
        self.match = match
        self.allow_call = allow_call
        self.allow_register = allow_register
        self.allow_publish = allow_publish
        self.allow_subscribe = allow_subscribe
        self.disclose_caller = disclose_caller
        self.disclose_publisher = disclose_publisher
        self.cache = cache
        self.created = created
        self.owner = owner

        # private member with unknown/untouched data passing through
        self._unknown = _unknown

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if not ConfigurationElement.__eq__(self, other):
            return False
        if other.role_oid != self.role_oid:
            return False
        if other.uri != self.uri:
            return False
        if other.uri_check_level != self.uri_check_level:
            return False
        if other.match != self.match:
            return False
        if other.allow_call != self.allow_call:
            return False
        if other.allow_register != self.allow_register:
            return False
        if other.allow_publish != self.allow_publish:
            return False
        if other.allow_subscribe != self.allow_subscribe:
            return False
        if other.disclose_caller != self.disclose_caller:
            return False
        if other.disclose_publisher != self.disclose_publisher:
            return False
        if other.cache != self.cache:
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

        :param other: Other permission to copy data from.
        :type other: instance of :class:`ManagementRealm`
        :return:
        """
        ConfigurationElement.copy(self, other, overwrite=overwrite)

        if (not self.role_oid and other.role_oid) or overwrite:
            self.role_oid = other.role_oid
        if (not self.uri and other.uri) or overwrite:
            self.uri = other.uri
        if (not self.uri_check_level and other.uri_check_level) or overwrite:
            self.uri_check_level = other.uri_check_level
        if (not self.match and other.match) or overwrite:
            self.match = other.match
        if (not self.allow_call and other.allow_call) or overwrite:
            self.allow_call = other.allow_call
        if (not self.allow_register and other.allow_register) or overwrite:
            self.allow_register = other.allow_register
        if (not self.allow_publish and other.allow_publish) or overwrite:
            self.allow_publish = other.allow_publish
        if (not self.allow_subscribe and other.allow_subscribe) or overwrite:
            self.allow_subscribe = other.allow_subscribe
        if (not self.disclose_caller and other.disclose_caller) or overwrite:
            self.disclose_caller = other.disclose_caller
        if (not self.disclose_publisher and other.disclose_publisher) or overwrite:
            self.disclose_publisher = other.disclose_publisher
        if (not self.cache and other.cache) or overwrite:
            self.cache = other.cache
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
            'oid':
            str(self.oid) if self.oid else None,
            'role_oid':
            str(self.role_oid) if self.role_oid else None,
            'uri':
            self.uri,
            'uri_check_level':
            Permission.URI_CHECK_LEVELS_TOSTR[self.uri_check_level] if self.uri_check_level else None,
            'match':
            Permission.MATCH_TYPES_TOSTR[self.match] if self.match else None,
            'allow_call':
            self.allow_call,
            'allow_register':
            self.allow_register,
            'allow_publish':
            self.allow_publish,
            'allow_subscribe':
            self.allow_subscribe,
            'disclose_caller':
            self.disclose_caller,
            'disclose_publisher':
            self.disclose_publisher,
            'cache':
            self.cache,
            'created':
            int(self.created) if self.created else None,
            'owner':
            str(self.owner) if self.owner else None,
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
            if k not in [
                    'oid', 'role_oid', 'uri', 'uri_check_level', 'match', 'allow_call', 'allow_register',
                    'allow_publish', 'allow_subscribe', 'disclose_caller', 'disclose_publisher', 'cache',
                    'owner', 'created'
            ]:
                _unknown[k] = data[k]

        role_oid = data.get('role_oid', None)
        assert role_oid is None or type(role_oid) == str
        if role_oid:
            role_oid = UUID(role_oid)

        uri = data.get('uri', None)
        assert uri is None or type(uri) == str

        uri_check_level = data.get('uri_check_level', None)
        assert uri_check_level is None or type(uri_check_level) == str
        if uri_check_level:
            assert uri_check_level in Permission.URI_CHECK_LEVELS_FROMSTR
            uri_check_level = Permission.URI_CHECK_LEVELS_FROMSTR[uri_check_level]

        match = data.get('match', None)
        assert match is None or type(match) == str
        if match:
            assert match in Permission.MATCH_TYPES_FROMSTR
            match = Permission.MATCH_TYPES_FROMSTR[match]

        allow_call = data.get('allow_call', None)
        assert allow_call is None or type(allow_call) == bool

        allow_register = data.get('allow_register', None)
        assert allow_register is None or type(allow_register) == bool

        allow_publish = data.get('allow_publish', None)
        assert allow_publish is None or type(allow_publish) == bool

        allow_subscribe = data.get('allow_subscribe', None)
        assert allow_subscribe is None or type(allow_subscribe) == bool

        disclose_caller = data.get('disclose_caller', None)
        assert disclose_caller is None or type(disclose_caller) == bool

        disclose_publisher = data.get('disclose_publisher', None)
        assert disclose_publisher is None or type(disclose_publisher) == bool

        cache = data.get('cache', None)
        assert cache is None or type(cache) == bool

        created = data.get('created', None)
        assert created is None or type(created) == int
        if created:
            created = np.datetime64(created, 'ns')

        owner = data.get('owner', None)
        assert owner is None or type(owner) == str
        if owner:
            owner = UUID(owner)

        obj = Permission(oid=obj.oid,
                         label=obj.label,
                         description=obj.description,
                         tags=obj.tags,
                         role_oid=role_oid,
                         uri=uri,
                         uri_check_level=uri_check_level,
                         match=match,
                         allow_call=allow_call,
                         allow_register=allow_register,
                         allow_publish=allow_publish,
                         allow_subscribe=allow_subscribe,
                         disclose_caller=disclose_caller,
                         disclose_publisher=disclose_publisher,
                         cache=cache,
                         created=created,
                         owner=owner,
                         _unknown=_unknown)

        return obj
