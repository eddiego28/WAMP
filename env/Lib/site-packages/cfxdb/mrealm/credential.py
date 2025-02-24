##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################

from typing import Optional
import pprint
import binascii
from uuid import UUID

import numpy as np

from cfxdb._exception import InvalidConfigException


class Credential(object):
    """
    Credentials created for use with WAMP authentication.
    """
    def __init__(self,
                 oid: Optional[UUID] = None,
                 created: Optional[np.datetime64] = None,
                 authmethod: Optional[str] = None,
                 authid: Optional[str] = None,
                 realm: Optional[str] = None,
                 authconfig: Optional[dict] = None,
                 principal_oid: Optional[UUID] = None,
                 _unknown=None):
        """

        :param oid: Object ID of this credential object

        :param created: Timestamp when credential was created.

        :param authmethod: WAMP authentication method offered by the authenticating client.

        :param realm: WAMP realm requested by the authenticating client.

        :param authid: WAMP authid announced by the authenticating client.

        :param authconfig: Authentication method specific configuration.

        :param principal_oid: ID of the principal this credential resolves to upon successful authentication.
        """
        self.oid = oid
        self.created = created
        self.authmethod = authmethod
        self.realm = realm
        self.authid = authid
        self.authconfig = authconfig
        self.principal_oid = principal_oid

        # private member with unknown/untouched data passing through
        self._unknown = _unknown

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if other.oid != self.oid:
            return False
        if other.created != self.created:
            return False
        if other.authmethod != self.authmethod:
            return False
        if other.realm != self.realm:
            return False
        if other.authid != self.authid:
            return False
        if other.authconfig != self.authconfig:
            return False
        if other.principal_oid != self.principal_oid:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return pprint.pformat(self.marshal())

    def copy(self, other, overwrite=False):
        """
        Copy over other object.

        :param other: Other credential to copy data from.
        :type other: instance of :class:`ManagementRealm`
        :return:
        """
        if (not self.oid and other.oid) or overwrite:
            self.oid = other.oid
        if (not self.created and other.created) or overwrite:
            self.created = other.created
        if (not self.authmethod and other.authmethod) or overwrite:
            self.authmethod = other.authmethod
        if (not self.realm and other.realm) or overwrite:
            self.realm = other.realm
        if (not self.authid and other.authid) or overwrite:
            self.authid = other.authid
        if (not self.authconfig and other.authconfig) or overwrite:
            self.authconfig = other.authconfig
        if (not self.principal_oid and other.principal_oid) or overwrite:
            self.principal_oid = other.principal_oid

        # _unknown is not copied!

    def marshal(self):
        """
        Marshal this object to a generic host language object.

        :return: dict
        """
        obj = {
            'oid': str(self.oid) if self.oid else None,
            'created': int(self.created) if self.created else None,
            'authmethod': self.authmethod,
            'realm': self.realm,
            'authid': self.authid,
            'authconfig': self.authconfig,
            'principal_oid': str(self.principal_oid) if self.principal_oid else None,
        }

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

        # future attributes (yet unknown) are not only ignored, but passed through!
        _unknown = {}
        for k in data:
            if k not in ['oid', 'created', 'authmethod', 'realm', 'authid', 'authconfig', 'principal_oid']:
                _unknown[k] = data[k]

        oid = data.get('oid', None)
        assert oid is None or type(oid) == str
        if oid:
            oid = UUID(oid)

        created = data.get('created', None)
        assert created is None or type(created) == int
        if created:
            created = np.datetime64(created, 'ns')

        authmethod = data.get('authmethod', None)
        assert authmethod is None or type(authmethod) == str

        realm = data.get('realm', None)
        assert realm is None or type(realm) == str

        authid = data.get('authid', None)
        assert authid is None or type(authid) == str

        principal_oid = data.get('principal_oid', None)
        assert principal_oid is None or type(principal_oid) == str
        if principal_oid:
            principal_oid = UUID(principal_oid)

        authconfig = data.get('authconfig', None)
        assert authconfig is None or type(authconfig) == dict

        if authconfig:
            if authmethod == 'cryptosign':
                # check allowed keys
                for key in authconfig:
                    if key not in ['authorized_keys']:
                        raise InvalidConfigException(
                            'invalid attribute "{}" in cryptosign config'.format(key))

                # check required keys
                if 'authorized_keys' not in authconfig or type(authconfig['authorized_keys']) != list:
                    raise InvalidConfigException(
                        'invalid type "{}" for authorized_keys in cryptosign config'.format(
                            type(authconfig['authorized_keys'])))
                if len(authconfig['authorized_keys']) == 0:
                    raise InvalidConfigException(
                        'need at least one key in authorized_keys in cryptosign config')
                authorized_keys = authconfig['authorized_keys']
                for k in authorized_keys:
                    if type(k) != str or len(k) != 64:
                        raise InvalidConfigException(
                            'key in autheorized_keys must have type str[64] (was {}) in authorized_keys in cryptosign config'
                            .format(type(k)))
                    try:
                        binascii.a2b_hex(k)
                    except Exception as e:
                        raise InvalidConfigException(
                            'invalid key in autheorized_keys in authorized_keys in cryptosign config: {}'.
                            format(e))

            elif authmethod == 'ticket':
                # check allowed keys
                for key in authconfig:
                    if key not in ['secret']:
                        raise InvalidConfigException('invalid attribute "{}" in ticket config'.format(key))

                # check required keys
                if 'secret' not in authconfig or type(authconfig['secret']) != str:
                    raise InvalidConfigException(
                        'invalid type "{}" for authorized_keys in ticket config'.format(
                            type(authconfig['authorized_keys'])))

            elif authmethod == 'wampcra':
                # check allowed keys
                for key in authconfig:
                    if key not in ['secret', 'salt', 'iterations', 'keylen']:
                        raise InvalidConfigException('invalid attribute "{}" in wampcra config'.format(key))

                # check required keys
                if 'secret' not in authconfig or type(authconfig['secret']) != str:
                    raise InvalidConfigException('invalid type "{}" for secret in wampcra config'.format(
                        type(authconfig['secret'])))
                if 'salt' in authconfig and type(authconfig['salt']) != str:
                    raise InvalidConfigException('invalid type "{}" for salt in wampcra config'.format(
                        type(authconfig['salt'])))
                if 'iterations' in authconfig and type(authconfig['iterations']) != int:
                    raise InvalidConfigException('invalid type "{}" for iterations in wampcra config'.format(
                        type(authconfig['iterations'])))
                if 'keylen' in authconfig and type(authconfig['keylen']) != int:
                    raise InvalidConfigException('invalid type "{}" for keylen in wampcra config'.format(
                        type(authconfig['keylen'])))

            elif authmethod == 'tls':
                raise NotImplementedError('FIXME: check tls authmethod configuration')

            elif authmethod == 'scram':
                # check allowed keys
                for key in authconfig:
                    if key not in ['kdf', 'iterations', 'memory', 'salt', 'stored-key', 'server-key']:
                        raise InvalidConfigException('invalid attribute "{}" in scram config'.format(key))

                # check required keys
                for key, Type in [('kdf', str), ('iterations', int), ('memory', int), ('salt', str),
                                  ('stored-key', str), ('server-key', str)]:
                    if key not in authconfig or type(authconfig[key]) != Type:
                        raise InvalidConfigException('invalid type "{}" for secret in scram config'.format(
                            type(authconfig[key])))

            elif authmethod == 'cookie':
                raise NotImplementedError('FIXME: check cookie authmethod configuration')

            elif authmethod == 'anonymous':
                # there is nothing to configure for authmethod==anonymous (authid/authrole actually assigned
                # is defined already "outside" this config dict)
                for key in authconfig:
                    if key not in []:
                        raise InvalidConfigException('invalid attribute "{}" in anonymous config'.format(key))
            else:
                raise InvalidConfigException('invalid authmethod "{}"'.format(authmethod))

        obj = Credential(oid=oid,
                         created=created,
                         authmethod=authmethod,
                         realm=realm,
                         authid=authid,
                         authconfig=authconfig,
                         principal_oid=principal_oid,
                         _unknown=_unknown)

        return obj
