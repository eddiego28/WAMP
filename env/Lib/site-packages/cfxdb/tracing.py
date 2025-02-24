##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################

import uuid
import pprint
from datetime import datetime

from zlmdb import table, MapUuidTimestampCbor

from .common import ConfigurationElement
from .mrealm import ManagementRealm


class TracedMessage(object):
    """
    CFC management realm database configuration object.
    """

    RTYPE_MREALM = 1
    RTYPE_APP = 2

    def __init__(self,
                 oid=None,
                 label=None,
                 description=None,
                 tags=None,
                 name=None,
                 created=None,
                 owner=None,
                 cf_node=None,
                 cf_router_worker=None,
                 cf_container_worker=None,
                 _unknown=None):
        """

        :param oid: Object ID of management realm
        :type oid: uuid.UUID

        :param label: Optional user label of management realm
        :type label: str

        :param description: Optional user description of management realm
        :type description: str

        :param tags: Optional list of user tags on management realm
        :type tags: list[str]

        :param name: Name of management realm
        :type name: str

        :param created: Timestamp when the management realm was created
        :type created: datetime.datetime

        :param owner: Owning user (object ID)
        :type owner: uuid.UUID

        :param cf_node: *INTERNAL USE* CFC hosting node for this management realm
        :type cf_node: str

        :param cf_router_worker: *INTERNAL USE* CFC hosting router worker for this management realm
        :type cf_router_worker: str

        :param cf_container_worker: *INTERNAL USE* CFC hosting container worker for this management realm
        :type cf_container_worker: str

        :param _unknown: Any unparsed/unprocessed data attributes
        :type _unknown: None or dict
        """
        ConfigurationElement.__init__(self, oid=oid, label=label, description=description, tags=tags)
        self.name = name
        self.created = created
        self.owner = owner
        self.cf_node = cf_node
        self.cf_router_worker = cf_router_worker
        self.cf_container_worker = cf_container_worker

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
        if other.cf_node != self.cf_node:
            return False
        if other.cf_router_worker != self.cf_router_worker:
            return False
        if other.cf_container_worker != self.cf_container_worker:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return '\n{}\n'.format(pprint.pformat(self.marshal()))

    def copy(self, other, overwrite=False):
        """
        Copy over other object.

        :param other: Other management realm to copy data from.
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
        if (not self.cf_node and other.cf_node) or overwrite:
            self.cf_node = other.cf_node
        if (not self.cf_router_worker and other.cf_router_worker) or overwrite:
            self.cf_router_worker = other.cf_router_worker
        if (not self.cf_container_worker and other.cf_container_worker) or overwrite:
            self.cf_container_worker = other.cf_container_worker

        # _unknown is not copied!

    def marshal(self):
        """
        Marshal this object to a generic host language object.

        :return: dict
        """
        assert isinstance(self.oid, uuid.UUID)
        assert type(self.name) == str
        assert isinstance(self.created, datetime)
        assert isinstance(self.owner, uuid.UUID)
        assert self.cf_node is None or isinstance(self.cf_node, uuid.UUID)
        assert self.cf_router_worker is None or isinstance(self.cf_router_worker, uuid.UUID)
        assert self.cf_container_worker is None or isinstance(self.cf_container_worker, uuid.UUID)

        obj = ConfigurationElement.marshal(self)

        obj.update({
            'oid': str(self.oid),
            'name': self.name,
            'created': int(self.created.timestamp() * 1000000) if self.created else None,
            'owner': str(self.owner),
            'cf_node': str(self.cf_node) if self.cf_node else None,
            'cf_router_worker': str(self.cf_router_worker) if self.cf_router_worker else None,
            'cf_container_worker': str(self.cf_container_worker) if self.cf_container_worker else None,
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
                    'oid', 'name', 'rtype', 'owner', 'created', 'cf_node', 'cf_router_worker',
                    'cf_container_worker'
            ]:
                _unknown[k] = data[k]

        name = data.get('name', None)
        assert name is None or type(name) == str

        owner = data.get('owner', None)
        assert type(owner) == str
        owner = uuid.UUID(owner)

        created = data.get('created', None)
        assert created is None or type(created) == float or type(created) == int
        if created:
            created = datetime.utcfromtimestamp(float(created) / 1000000.)

        cf_node = data.get('cf_node', None)
        assert cf_node is None or type(cf_node) == str
        if cf_node:
            cf_node = uuid.UUID(cf_node)

        cf_router_worker = data.get('cf_router_worker', None)
        assert cf_router_worker is None or type(cf_router_worker) == str
        if cf_router_worker:
            cf_router_worker = uuid.UUID(cf_router_worker)

        cf_container_worker = data.get('cf_container_worker', None)
        assert cf_container_worker is None or type(cf_container_worker) == str
        if cf_container_worker:
            cf_container_worker = uuid.UUID(cf_container_worker)

        obj = ManagementRealm(oid=obj.oid,
                              label=obj.label,
                              description=obj.description,
                              tags=obj.tags,
                              name=name,
                              owner=owner,
                              created=created,
                              cf_node=cf_node,
                              cf_router_worker=cf_router_worker,
                              cf_container_worker=cf_container_worker,
                              _unknown=_unknown)

        return obj


@table('7ff23263-92da-4ca3-b249-0293788bcd4c', marshal=TracedMessage.marshal, parse=TracedMessage.parse)
class TracedMessages(MapUuidTimestampCbor):
    """
    Table: trace_oid, timestamp -> traced_message
    """
