##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################

from typing import Optional, List
import pprint
from uuid import UUID

from cfxdb.common import ConfigurationElement


class WebService(ConfigurationElement):
    """
    Web service:

    * check_web_path_service
    """
    def __init__(self,
                 oid: Optional[UUID] = None,
                 label: Optional[str] = None,
                 description: Optional[str] = None,
                 tags: Optional[List[str]] = None,
                 service_type: Optional[str] = None,
                 webcluster_oid: Optional[UUID] = None,
                 path: Optional[str] = None,
                 _unknown=None):
        """

        :param oid: Object ID of this web service.

        :param label: Optional user label of this web service.

        :param description: Optional user description of this web service.

        :param tags: Optional list of user tags on this web service.

        :param path: HTTP URL path of the Web service, eg ``/myapp`` or ``/myapp/dashboard/72``.
        """
        ConfigurationElement.__init__(self,
                                      oid=oid,
                                      label=label,
                                      description=description,
                                      tags=tags,
                                      _unknown=_unknown)
        self.service_type = service_type
        self.webcluster_oid = webcluster_oid
        self.path = path

    def other(self, key, default=None):
        return self._unknown.get(key, default)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if not ConfigurationElement.__eq__(self, other):
            return False
        if other.service_type != self.service_type:
            return False
        if other.webcluster_oid != self.webcluster_oid:
            return False
        if other.path != self.path:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return '\n{}\n'.format(pprint.pformat(self.marshal()))

    def marshal(self):
        """
        Marshal this object to a generic host language object.

        :return: dict
        """
        obj = ConfigurationElement.marshal(self)

        obj.update({
            'webcluster_oid': str(self.webcluster_oid),
            'path': self.path,
            'type': self.service_type,
        })

        if self._unknown:
            obj.update(self._unknown)

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

        obj = ConfigurationElement.parse(data)
        data = obj._unknown

        # future attributes (yet unknown) are not only ignored, but passed through!
        _unknown = {}
        for k in data:
            if k not in ['type', 'path', 'webcluster_oid']:
                _unknown[k] = data[k]

        webcluster_oid = data.get('webcluster_oid', None)
        assert webcluster_oid is None or (type(webcluster_oid) == str)
        if webcluster_oid:
            webcluster_oid = UUID(webcluster_oid)

        path = data.get('path', None)
        assert path is None or (type(path) == str)

        service_type = data.get('type', None)
        assert service_type is None or (type(service_type) == str)

        obj = WebService(oid=obj.oid,
                         label=obj.label,
                         description=obj.description,
                         tags=obj.tags,
                         service_type=service_type,
                         webcluster_oid=webcluster_oid,
                         path=path,
                         _unknown=_unknown)

        return obj
