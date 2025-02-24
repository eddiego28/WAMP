##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################

import struct
import uuid
from datetime import datetime
from pprint import pformat

from cfxdb.gen import oid_t
from cfxdb.gen.user import User as UserGenFbs


class UserFbs(object):
    """
    CFC user database class using Flatbuffers.
    """

    # oid: uuid.UUID

    # label: Optional[str]
    # description: Optional[str]
    # tags: Optional[List[str]]

    # email: str
    # registered: datetime
    # pubkey: str

    def __init__(self, from_fbs=None):
        self._from_fbs = from_fbs

        self._oid = None

        self._label = None
        self._description = None
        self._tags = None

        self._email = None
        self._registered = None
        self._pubkey = None

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        if other.oid != self.oid:
            return False

        if other.label != self.label:
            return False
        if other.description != self.description:
            return False
        if (other.tags and not self.tags) or (not other.tags and self.tags):
            return False
        if other.tags:
            if not set(other.tags).intersection(set(self.tags)):
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

    @property
    def oid(self):
        if self._oid is None and self._from_fbs:
            oid = self._from_fbs.Oid()
            if oid:
                bytes = struct.pack('>Q', oid.Lsb()) + struct.pack('>Q', oid.Msb())
                self._oid = uuid.UUID(bytes=bytes)
        return self._oid

    @oid.setter
    def oid(self, value):
        assert isinstance(value, uuid.UUID)

        self._oid = value

    @property
    def label(self):
        if self._label is None and self._from_fbs:
            s = self._from_fbs.Label()
            if s:
                self._label = s.decode()
        return self._label

    @label.setter
    def label(self, value):
        assert type(value) == str

        self._label = value

    @property
    def description(self):
        if self._description is None and self._from_fbs:
            s = self._from_fbs.Description()
            if s:
                self._description = s.decode()
        return self._description

    @description.setter
    def description(self, value):
        assert type(value) == str

        self._description = value

    @property
    def tags(self):
        if self._tags is None and self._from_fbs:
            if self._from_fbs.TagsLength() > 0:
                tags = []
                for i in range(self._from_fbs.TagsLength()):
                    s = self._from_fbs.Tags(i)
                    tags.append(s.decode())
                self._tags = tags
        return self._tags

    @tags.setter
    def tags(self, value):
        assert type(value) == list
        assert (type(tag) == str for tag in value)

        self._tags = value

    @property
    def email(self):
        if self._email is None and self._from_fbs:
            s = self._from_fbs.Email()
            if s:
                self._email = s.decode()
        return self._email

    @email.setter
    def email(self, value):
        assert type(value) == str

        self._email = value

    @property
    def registered(self):
        if self._registered is None and self._from_fbs:
            val = self._from_fbs.Registered()
            if val:
                # utcfromtimestamp
                # self._registered = datetime.utcfromtimestamp(float(val) / 1000000.)
                # calendar.timegm(dt.utctimetuple())
                self._registered = datetime.fromtimestamp(float(val) / 1000000.)

        return self._registered

    @registered.setter
    def registered(self, value):
        assert isinstance(value, datetime)

        self._registered = value

    @property
    def pubkey(self):
        if self._pubkey is None and self._from_fbs:
            self._pubkey = self._from_fbs.Pubkey().decode()

        return self._pubkey

    @pubkey.setter
    def pubkey(self, value):
        # hex string with 256 bit Ed25519 WAMP-cryptosign public key
        assert type(value) == str
        assert len(value) == 64

        self._pubkey = value

    @staticmethod
    def cast(buf):
        return UserFbs(UserGenFbs.User.GetRootAsUser(buf, 0))

    def build(self, builder):

        # serialize all stuff we need later first (because we cannot build nested) ..

        # label: string
        label = self.label
        if label:
            label = builder.CreateString(label)

        # description: string
        description = self.description
        if description:
            description = builder.CreateString(description)

        # email: string
        email = self.email
        if email:
            email = builder.CreateString(email)

        # pubkey: string
        pubkey = self.pubkey
        if pubkey:
            pubkey = builder.CreateString(pubkey)

        # tags: [string]
        tags = self.tags
        if tags:
            _tags = []
            for tag in tags:
                _tags.append(builder.CreateString(tag))

            UserGenFbs.UserStartTagsVector(builder, len(_tags))

            for o in reversed(_tags):
                builder.PrependUOffsetTRelative(o)

            tags = builder.EndVector()

        # now start and build a new object ..
        UserGenFbs.UserStart(builder)

        # oid: uuid.UUID
        if self.oid:
            bytes = self.oid.bytes
            msb = struct.unpack('>Q', bytes[8:])[0]
            lsb = struct.unpack('>Q', bytes[:8])[0]
            oid = oid_t.Createoid_t(builder, msb=msb, lsb=lsb)
            UserGenFbs.UserAddOid(builder, oid)

        if label:
            UserGenFbs.UserAddLabel(builder, label)
        if description:
            UserGenFbs.UserAddDescription(builder, description)
        if tags:
            UserGenFbs.UserAddTags(builder, tags)
        if email:
            UserGenFbs.UserAddEmail(builder, email)

        # registered: datetime
        if self.registered:
            registered = int(self.registered.timestamp() * 1000000)
            UserGenFbs.UserAddRegistered(builder, registered)

        if pubkey:
            UserGenFbs.UserAddPubkey(builder, pubkey)

        # finish the object.
        final = UserGenFbs.UserEnd(builder)

        return final
