##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################

from typing import Optional, List, Any, Dict
from uuid import UUID
import pprint

import numpy as np

from cfxdb.common import ConfigurationElement
from cfxdb.gen.arealm.ApplicationRealmStatus import ApplicationRealmStatus


class ApplicationRealm(ConfigurationElement):
    """
    Application realm database configuration object.
    """

    STATUS_BY_CODE = {
        ApplicationRealmStatus.NONE: 'NONE',
        ApplicationRealmStatus.STOPPED: 'STOPPED',
        ApplicationRealmStatus.STARTING: 'STARTING',
        ApplicationRealmStatus.RUNNING: 'RUNNING',
        ApplicationRealmStatus.PAUSED: 'PAUSED',
        ApplicationRealmStatus.STOPPING: 'STOPPING',
        ApplicationRealmStatus.ERROR: 'ERROR',
        ApplicationRealmStatus.DEGRADED: 'DEGRADED',
    }

    STATUS_BY_NAME = {
        'NONE': ApplicationRealmStatus.NONE,
        'STOPPED': ApplicationRealmStatus.STOPPED,
        'STARTING': ApplicationRealmStatus.STARTING,
        'RUNNING': ApplicationRealmStatus.RUNNING,
        'PAUSED': ApplicationRealmStatus.PAUSED,
        'STOPPING': ApplicationRealmStatus.STOPPING,
        'ERROR': ApplicationRealmStatus.ERROR,
        'DEGRADED': ApplicationRealmStatus.DEGRADED,
    }

    STATUS_STOPPED = ApplicationRealmStatus.STOPPED
    STATUS_STARTING = ApplicationRealmStatus.STARTING
    STATUS_RUNNING = ApplicationRealmStatus.RUNNING
    STATUS_PAUSED = ApplicationRealmStatus.PAUSED
    STATUS_STOPPING = ApplicationRealmStatus.STOPPING
    STATUS_ERROR = ApplicationRealmStatus.ERROR
    STATUS_DEGRADED = ApplicationRealmStatus.DEGRADED

    def __init__(self,
                 oid: Optional[UUID] = None,
                 label: Optional[str] = None,
                 description: Optional[str] = None,
                 tags: Optional[List[str]] = None,
                 name: Optional[str] = None,
                 status: Optional[int] = None,
                 workergroup_oid: Optional[UUID] = None,
                 webcluster_oid: Optional[UUID] = None,
                 datamarket_oid: Optional[UUID] = None,
                 changed: Optional[np.datetime64] = None,
                 owner_oid: Optional[UUID] = None,
                 _unknown: Optional[Any] = None):
        """

        :param oid: Object ID of application realm

        :param label: Optional user label of application realm

        :param description: Optional user description of application realm

        :param tags: Optional list of user tags on application realm

        :param name: Name of application realm

        :param status: Status of application realm.

        :param workergroup_oid: When running, router cluster worker group this application
            realm is running on.

        :param webcluster_oid: When running, the web cluster to serve as a frontend layer
            for the application realm.

        :param datamarket_oid: When this application realm is to be federated with nodes paired
            to a different management realm (master node) or run by different operators.

        :param changed: Timestamp when the application realm was last changed

        :param owner_oid: Owning user (object ID)
        """
        ConfigurationElement.__init__(self, oid=oid, label=label, description=description, tags=tags)
        self.name = name
        self.status = status
        self.workergroup_oid = workergroup_oid
        self.webcluster_oid = webcluster_oid
        self.datamarket_oid = datamarket_oid
        self.changed = changed
        self.owner_oid = owner_oid

        # private member with unknown/untouched data passing through
        self._unknown = _unknown

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        if not ConfigurationElement.__eq__(self, other):
            return False
        if other.name != self.name:
            return False
        if other.status != self.status:
            return False
        if other.workergroup_oid != self.workergroup_oid:
            return False
        if other.webcluster_oid != self.webcluster_oid:
            return False
        if other.datamarket_oid != self.datamarket_oid:
            return False
        if other.changed != self.changed:
            return False
        if other.owner_oid != self.owner_oid:
            return False
        return True

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __str__(self) -> str:
        return pprint.pformat(self.marshal())

    def copy(self, other: 'ApplicationRealm', overwrite: bool = False):
        """
        Copy over other object.

        :param other: Other application realm to copy data from.
        :param overwrite: Overwrite members already set.
        """
        ConfigurationElement.copy(self, other, overwrite=overwrite)

        if (not self.name and other.name) or overwrite:
            self.name = other.name
        if (not self.status and other.status) or overwrite:
            self.status = other.status
        if (not self.workergroup_oid and other.workergroup_oid) or overwrite:
            self.workergroup_oid = other.workergroup_oid
        if (not self.webcluster_oid and other.webcluster_oid) or overwrite:
            self.webcluster_oid = other.webcluster_oid
        if (not self.datamarket_oid and other.datamarket_oid) or overwrite:
            self.datamarket_oid = other.datamarket_oid
        if (not self.changed and other.changed) or overwrite:
            self.changed = other.changed
        if (not self.owner_oid and other.owner_oid) or overwrite:
            self.owner_oid = other.owner_oid

        # _unknown is not copied!

    def marshal(self) -> Dict[str, Any]:
        """
        Marshal this object to a generic host language object.
        """
        obj = ConfigurationElement.marshal(self)

        obj.update({
            'oid':
            str(self.oid) if self.oid else None,
            'name':
            self.name,
            'status':
            ApplicationRealm.STATUS_BY_CODE[self.status]
            if self.status in ApplicationRealm.STATUS_BY_CODE else None,
            'workergroup_oid':
            str(self.workergroup_oid) if self.workergroup_oid else None,
            'webcluster_oid':
            str(self.webcluster_oid) if self.webcluster_oid else None,
            'datamarket_oid':
            str(self.datamarket_oid) if self.datamarket_oid else None,
            'changed':
            int(self.changed) if self.changed else None,
            'owner_oid':
            str(self.owner_oid) if self.owner_oid else None,
        })

        if self._unknown:
            # pass through all attributes unknown
            obj.update(self._unknown)

        return obj

    @staticmethod
    def parse(data: Dict[str, Any]) -> 'ApplicationRealm':
        """
        Parse generic host language object into an object of this class.

        :param data: Generic host language object
        :returns: New instance of this class.
        """
        assert type(data) == dict

        obj = ConfigurationElement.parse(data)
        data = obj._unknown

        # future attributes (yet unknown) are not only ignored, but passed through!
        _unknown = {}
        for k in data:
            if k not in [
                    'oid', 'name', 'status', 'workergroup_oid', 'webcluster_oid', 'owner_oid', 'changed'
            ]:
                _unknown[k] = data[k]

        name = data.get('name', 'arealm-{}'.format(str(obj.oid)[:8]))
        assert type(name) == str

        status = data.get('status', None)
        assert status is None or (type(status) == str)
        status = ApplicationRealm.STATUS_BY_NAME[status] if status in ApplicationRealm.STATUS_BY_NAME else None

        workergroup_oid = None
        if 'workergroup_oid' in data and data['workergroup_oid'] is not None:
            assert type(
                data['workergroup_oid']) == str, 'workergroup_oid must be a string, but was {}'.format(
                    type(data['workergroup_oid']))
            workergroup_oid = UUID(data['workergroup_oid'])

        webcluster_oid = None
        if 'webcluster_oid' in data and data['webcluster_oid'] is not None:
            assert type(data['webcluster_oid']) == str, 'webcluster_oid must be a string, but was {}'.format(
                type(data['webcluster_oid']))
            webcluster_oid = UUID(data['webcluster_oid'])

        datamarket_oid = None
        if 'datamarket_oid' in data and data['datamarket_oid'] is not None:
            assert type(data['datamarket_oid']) == str, 'datamarket_oid must be a string, but was {}'.format(
                type(data['datamarket_oid']))
            datamarket_oid = UUID(data['datamarket_oid'])

        owner_oid = None
        if 'owner_oid' in data and data['owner_oid'] is not None:
            assert type(data['owner_oid']) == str, 'owner_oid must be a string, but was {}'.format(
                type(data['owner_oid']))
            owner_oid = UUID(data['owner_oid'])

        changed = data.get('changed', None)
        assert changed is None or type(changed) == int
        if changed:
            changed = np.datetime64(changed, 'ns')

        obj = ApplicationRealm(oid=obj.oid,
                               label=obj.label,
                               description=obj.description,
                               tags=obj.tags,
                               name=name,
                               workergroup_oid=workergroup_oid,
                               webcluster_oid=webcluster_oid,
                               datamarket_oid=datamarket_oid,
                               status=status,
                               owner_oid=owner_oid,
                               changed=changed,
                               _unknown=_unknown)

        return obj
