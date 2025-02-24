##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################

from uuid import UUID
from datetime import datetime
from pprint import pformat
from typing import Optional, List

from cfxdb.common import ConfigurationElement


class User(ConfigurationElement):
    """
    Users registered with this master instance.

    .. note::
        The user database exists "globally" (master-wide) and
        independent of management realms. A given user can be owner or authorized to
        access different management realms or resources therein.
    """
    def __init__(self,
                 oid: Optional[UUID] = None,
                 label: Optional[str] = None,
                 description: Optional[str] = None,
                 tags: Optional[List[str]] = None,
                 email: Optional[str] = None,
                 registered: Optional[datetime] = None,
                 pubkey: Optional[str] = None,
                 _unknown=None):
        """

        :param oid: Object ID of the user

        :param label: Optional user label of the user

        :param description: Optional user description of the user

        :param tags: Optional list of user tags on the user

        :param email: User email

        :param registered: Timestamp when the user registered

        :param pubkey: Public key of user (HEX encoded Ed25519 32 byte public key).
        """

        ConfigurationElement.__init__(self, oid=oid, label=label, description=description, tags=tags)

        self.email = email
        self.registered = registered
        self.pubkey = pubkey

        # private member with unknown/untouched data passing through
        self._unknown = _unknown

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        if not ConfigurationElement.__eq__(self, other):
            return False

        if other.email != self.email:
            return False
        if other.registered != self.registered:
            return False
        if other.pubkey != self.pubkey:
            return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return '\n{}\n'.format(pformat(self.marshal()))

    def copy(self, other):
        self.oid = other.oid
        self.label = other.label
        self.description = other.description
        self.tags = other.tags
        self.email = other.email
        self.registered = other.registered
        self.pubkey = other.pubkey

        # _unknown is not copied!

    def marshal(self):
        obj = ConfigurationElement.marshal(self)

        assert self.email is None or type(self.email) == str
        assert self.registered is None or isinstance(self.registered, datetime)
        assert self.pubkey is None or (type(self.pubkey) == str and len(self.pubkey) == 64)

        registered = int(self.registered.timestamp() * 1000000) if self.registered else None
        obj.update({
            'email': self.email,
            'registered': registered,
            'pubkey': self.pubkey,
        })

        if self._unknown:
            # pass through all attributes unknown
            obj.update(self._unknown)

        return obj

    @staticmethod
    def parse(data):
        assert type(data) == dict

        obj = ConfigurationElement.parse(data)
        data = obj._unknown

        # future attributes (yet unknown) are not only ignored, but passed through!
        _unknown = {}
        for k in data:
            if k not in ['email', 'registered', 'pubkey']:
                val = data.pop(k)
                _unknown[k] = val

        email = data.get('email', None)
        assert email is None or type(email) == str

        registered = data.get('registered', None)
        assert registered is None or type(registered) == float or type(registered) == int
        if registered:
            # registered = datetime.utcfromtimestamp(float(registered) / 1000000.)
            registered = datetime.fromtimestamp(float(registered) / 1000000.)

        # hex string with 256 bit Ed25519 WAMP-cryptosign public key
        pubkey = data.get('pubkey', None)
        assert pubkey is None or (type(pubkey) == str and len(pubkey) == 64)

        obj = User(oid=obj.oid,
                   label=obj.label,
                   description=obj.description,
                   tags=obj.tags,
                   email=email,
                   registered=registered,
                   pubkey=pubkey,
                   _unknown=_unknown)
        return obj
