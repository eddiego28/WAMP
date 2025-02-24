##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################

import uuid
from datetime import datetime

from cfxdb.gen.user import ActivationToken as ActivationTokenGenFbs
from cfxdb.gen.user.ActivationStatus import ActivationStatus
from cfxdb.gen.user.ActivationType import ActivationType


class ActivationTokenFbs(object):
    """
    CFC user activation token database class for Flatbuffers.
    """
    def __init__(self, from_fbs=None):
        self._from_fbs = from_fbs

        self._oid = None
        self._atype = None
        self._status = None
        self._created = None
        self._completed = None
        self._code = None
        self._email = None
        self._pubkey = None

    def copy(self, other):
        self._oid = other.oid
        self._atype = other.atype
        self._status = other.status
        self._created = other.created
        self._completed = other.completed
        self._code = other.code
        self._email = other.email
        self._pubkey = other.pubkey

    @property
    def oid(self):
        if self._oid is None and self._from_fbs:
            s = self._from_fbs.Oid()
            if s:
                self._oid = uuid.UUID(s.decode())

        return self._oid

    @oid.setter
    def oid(self, value):
        assert isinstance(value, uuid.UUID)

        self._oid = value

    @property
    def atype(self):
        if self._atype is None and self._from_fbs:
            self._atype = self._from_fbs.Atype()

        return self._atype

    @atype.setter
    def atype(self, value):
        assert type(value) == int
        assert value in [ActivationType.REGISTRATION, ActivationType.LOGIN]

        self._atype = value

    @property
    def status(self):
        if self._status is None and self._from_fbs:
            self._status = self._from_fbs.Status()

        return self._status

    @status.setter
    def status(self, value):
        assert type(value) == int
        assert value in [ActivationStatus.PENDING, ActivationStatus.ACTIVE, ActivationStatus.EXPIRED]

        self._status = value

    @property
    def created(self):
        if self._created is None and self._from_fbs:
            val = self._from_fbs.Created()
            if val:
                self._created = datetime.utcfromtimestamp(float(val) / 1000000.)

        return self._created

    @created.setter
    def created(self, value):
        assert isinstance(value, datetime)

        self._created = value

    @property
    def completed(self):
        if self._completed is None and self._from_fbs:
            val = self._from_fbs.Completed()
            if val:
                self._completed = datetime.utcfromtimestamp(float(val) / 1000000.)

        return self._completed

    @completed.setter
    def completed(self, value):
        assert value is None or isinstance(value, datetime)

        self._completed = value

    @property
    def code(self):
        if self._code is None and self._from_fbs:
            self._code = self._from_fbs.Code().decode()

        return self._code

    @code.setter
    def code(self, value):
        assert type(value) == str

        self._code = value

    @property
    def email(self):
        if self._email is None and self._from_fbs:
            self._email = self._from_fbs.Email().decode()

        return self._email

    @email.setter
    def email(self, value):
        assert type(value) == str

        self._email = value

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
        return ActivationTokenFbs(ActivationTokenGenFbs.ActivationToken.GetRootAsActivationToken(buf, 0))

    def build(self, builder):

        oid = self.oid
        if oid:
            oid = builder.CreateString(str(oid))

        code = self.code
        if code:
            code = builder.CreateString(code)

        email = self.email
        if email:
            email = builder.CreateString(email)

        pubkey = self.pubkey
        if pubkey:
            pubkey = builder.CreateString(pubkey)

        ActivationTokenGenFbs.ActivationTokenStart(builder)

        if oid:
            ActivationTokenGenFbs.ActivationTokenAddOid(builder, oid)

        ActivationTokenGenFbs.ActivationTokenAddAtype(builder, self.atype)
        ActivationTokenGenFbs.ActivationTokenAddStatus(builder, self.status)

        if self.created:
            ActivationTokenGenFbs.ActivationTokenAddCreated(builder, int(self.created.timestamp() * 1000000))

        if self.completed:
            ActivationTokenGenFbs.ActivationTokenAddCompleted(builder,
                                                              int(self.completed.timestamp() * 1000000))

        if code:
            ActivationTokenGenFbs.ActivationTokenAddCode(builder, code)

        if email:
            ActivationTokenGenFbs.ActivationTokenAddEmail(builder, email)

        if pubkey:
            ActivationTokenGenFbs.ActivationTokenAddPubkey(builder, pubkey)

        final = ActivationTokenGenFbs.ActivationTokenEnd(builder)

        return final
