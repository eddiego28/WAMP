##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################

import uuid
from datetime import datetime
from pprint import pformat

from cfxdb.gen.user.ActivationStatus import ActivationStatus
from cfxdb.gen.user.ActivationType import ActivationType


class ActivationToken(object):
    """
    CFC user activation token database class for CBOR.
    """
    def __init__(self,
                 oid=None,
                 atype=None,
                 status=None,
                 created=None,
                 completed=None,
                 code=None,
                 email=None,
                 pubkey=None,
                 _unknown=None):
        self.oid = oid
        self.atype = atype
        self.status = status
        self.created = created
        self.completed = completed
        self.code = code
        self.email = email
        self.pubkey = pubkey

        self._unknown = _unknown

    def __str__(self):
        return pformat(self.marshal())

    def copy(self, other):
        self.oid = other.oid
        self.atype = other.atype
        self.status = other.status
        self.created = other.created
        self.completed = other.completed
        self.code = other.code
        self.email = other.email
        self.pubkey = other.pubkey

        # _unknown is not copied!

    def marshal(self):
        assert isinstance(self.oid, uuid.UUID)
        assert self.atype in [ActivationType.LOGIN, ActivationType.REGISTRATION]
        assert self.status in [ActivationStatus.EXPIRED, ActivationStatus.PENDING, ActivationStatus.ACTIVE]
        assert isinstance(self.created, datetime)
        assert self.completed is None or isinstance(self.completed, datetime)
        assert self.code is None or type(self.code) == str
        assert self.email is None or type(self.email) == str
        assert self.pubkey is None or (type(self.pubkey) == str and len(self.pubkey) == 64)
        assert self._unknown is None or type(self._unknown) == dict

        created = float(self.created.timestamp()) * 1000000.
        completed = None
        if self.completed:
            completed = float(self.completed.timestamp()) * 1000000.

        obj = {
            u'oid': str(self.oid),
            u'atype': self.atype,
            u'status': self.status,
            u'created': created,
            u'completed': completed,
            u'code': self.code,
            u'email': self.email,
            u'pubkey': self.pubkey
        }

        if self._unknown:
            # pass through all attributes unknown
            obj.update(self._unknown)
        else:
            return obj

    @staticmethod
    def parse(data):
        assert type(data) == dict

        # future attributes (yet unknown) are not only ignored, but passed through!
        _unknown = {}
        for k in data:
            if k not in ['oid', 'atype', 'status', 'created', 'completed', 'code', 'email', 'pubkey']:
                val = data.pop(k)
                _unknown[k] = val

        oid = data.get('oid', None)
        assert type(oid) == str
        oid = uuid.UUID(oid)

        atype = data.get('atype', None)
        assert type(atype) == int

        status = data.get('status', None)
        assert type(status) == int

        created = data.get('created', None)
        assert type(created) == float or type(created) == int

        created = datetime.fromtimestamp(float(created) / 1000000.)
        # created = datetime.utcfromtimestamp(float(created) / 1000000.)

        completed = data.get('completed', None)
        assert completed is None or type(completed) == float or type(completed) == int
        if completed:
            # https://docs.python.org
            # /3/library/time.html#time.time_ns
            # https://docs.python.org/3/library/datetime.html#datetime.datetime.timestamp

            completed = datetime.fromtimestamp(float(completed) / 1000000.)
            # completed = datetime.utcfromtimestamp(float(completed) / 1000000.)

        code = data.get('code', None)
        assert type(code) == str

        email = data.get('email', None)
        assert email is None or type(email) == str

        pubkey = data.get('pubkey', None)
        assert pubkey is None or type(pubkey) == str
        if pubkey:
            assert len(pubkey) == 64

        obj = ActivationToken(oid=oid,
                              atype=atype,
                              status=status,
                              created=created,
                              completed=completed,
                              code=code,
                              email=email,
                              pubkey=pubkey,
                              _unknown=_unknown)
        return obj
