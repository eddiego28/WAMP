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
from cfxdb.gen.user import Organization as OrganizationGenFbs


class OrganizationFbs(object):
    """
    CFC user database class using Flatbuffers.
    """

    # oid: uuid.UUID

    # label: Optional[str]
    # description: Optional[str]
    # tags: Optional[List[str]]

    # name: str
    # registered: datetime
    # otype: int

    def __init__(self, from_fbs=None):
        self._from_fbs = from_fbs

        self._oid = None

        self._label = None
        self._description = None
        self._tags = None

        self._name = None
        self._otype = None
        self._registered = None

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

        if other.name != self.name:
            return False
        if other.otype != self.otype:
            return False
        if other.registered != self.registered:
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
        self.name = other.name
        self.otype = other.otype
        self.registered = other.registered

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
        assert value is None or isinstance(value, uuid.UUID)

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
        assert value is None or type(value) == str

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
        assert value is None or type(value) == str

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
        assert value is None or (type(value) == list and (type(tag) == str for tag in value))

        self._tags = value

    @property
    def name(self):
        if self._name is None and self._from_fbs:
            s = self._from_fbs.Name()
            if s:
                self._name = s.decode()
        return self._name

    @name.setter
    def name(self, value):
        assert value is None or type(value) == str

        self._name = value

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
        assert value is None or isinstance(value, datetime)

        self._registered = value

    @property
    def otype(self):
        if self._otype is None and self._from_fbs:
            self._otype = self._from_fbs.Otype()

        return self._otype

    @otype.setter
    def otype(self, value):
        assert value is None or type(value) == int

        self._otype = value

    @staticmethod
    def cast(buf):
        return OrganizationFbs(OrganizationGenFbs.Organization.GetRootAsOrganization(buf, 0))

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

        # name: string
        name = self.name
        if name:
            name = builder.CreateString(name)

        # tags: [string]
        tags = self.tags
        if tags:
            _tags = []
            for tag in tags:
                _tags.append(builder.CreateString(tag))

            OrganizationGenFbs.OrganizationStartTagsVector(builder, len(_tags))

            for o in reversed(_tags):
                builder.PrependUOffsetTRelative(o)

            tags = builder.EndVector()

        # now start and build a new object ..
        OrganizationGenFbs.OrganizationStart(builder)

        # oid: uuid.UUID
        if self.oid:
            bytes = self.oid.bytes
            msb = struct.unpack('>Q', bytes[8:])[0]
            lsb = struct.unpack('>Q', bytes[:8])[0]
            oid = oid_t.Createoid_t(builder, msb=msb, lsb=lsb)
            OrganizationGenFbs.OrganizationAddOid(builder, oid)

        if label:
            OrganizationGenFbs.OrganizationAddLabel(builder, label)
        if description:
            OrganizationGenFbs.OrganizationAddDescription(builder, description)
        if tags:
            OrganizationGenFbs.OrganizationAddTags(builder, tags)
        if name:
            OrganizationGenFbs.OrganizationAddName(builder, name)

        # registered: datetime
        if self.registered:
            registered = int(self.registered.timestamp() * 1000000)
            OrganizationGenFbs.OrganizationAddRegistered(builder, registered)

        if self.otype:
            OrganizationGenFbs.OrganizationAddOtype(builder, self.otype)

        # finish the object.
        final = OrganizationGenFbs.OrganizationEnd(builder)

        return final
