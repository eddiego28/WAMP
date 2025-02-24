##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################

from pprint import pformat
from cfxdb.gen.user.UserRole import UserRole


class UserMrealmRole(object):
    """
    Database class for CFC user roles on a management realm using CBOR.
    """
    def __init__(self, roles=None, _unknown=None):
        self.roles = roles

        # private member with unknown/untouched data passing through
        self._unknown = _unknown

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if other.roles != self.roles:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return '\n{}\n'.format(pformat(self.marshal()))

    def copy(self, other):
        self.roles = other.roles[:]

        # _unknown is not copied!

    def marshal(self):
        assert type(self.roles) == list
        for role in self.roles:
            assert type(role) == int
            assert role in [UserRole.OWNER, UserRole.ADMIN, UserRole.USER, UserRole.GUEST]

        obj = {
            'roles': self.roles,
        }

        if self._unknown:
            # pass through all attributes unknown
            obj.update(self._unknown)
        else:
            return obj

        return obj

    @staticmethod
    def parse(data):
        assert type(data) == dict

        # future attributes (yet unknown) are not only ignored, but passed through!
        _unknown = {}
        for k in data:
            if k not in ['roles']:
                _unknown[k] = data[k]

        roles = data.get('roles', None)
        assert type(roles) == list

        for role in roles:
            assert type(role) == int
            assert role in [UserRole.OWNER, UserRole.ADMIN, UserRole.USER, UserRole.GUEST]

        obj = UserMrealmRole(roles=roles, _unknown=_unknown)
        return obj
