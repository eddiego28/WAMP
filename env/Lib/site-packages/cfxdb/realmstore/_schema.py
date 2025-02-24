##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################

from typing import Optional

import zlmdb
from cfxdb.realmstore._session import Sessions, IndexSessionsBySessionId
from cfxdb.realmstore._publication import Publications
from cfxdb.realmstore._event import Events


class RealmStore(object):
    """
    Persistent realm store.
    """

    __slots__ = (
        '_db',
        '_sessions',
        '_idx_sessions_by_session_id',
        '_publications',
        '_events',
    )

    def __init__(self, db):
        self._db = db
        self._sessions: Optional[Sessions] = None
        self._idx_sessions_by_session_id: Optional[IndexSessionsBySessionId] = None
        self._publications: Optional[Publications] = None
        self._events: Optional[Events] = None

    @property
    def db(self) -> zlmdb.Database:
        """
        Database this schema is attached to.
        """
        return self._db

    @property
    def sessions(self) -> Optional[Sessions]:
        """
        Sessions persisted in this realm store.
        """
        return self._sessions

    @property
    def idx_sessions_by_session_id(self) -> Optional[IndexSessionsBySessionId]:
        """
        Index: (session, joined_at) -> app_session_oid
        """
        return self._idx_sessions_by_session_id

    @property
    def publications(self) -> Optional[Publications]:
        """
        Publications archive.
        """
        return self._publications

    @property
    def events(self) -> Optional[Events]:
        """
        Events archive.
        """
        return self._events

    @staticmethod
    def attach(db: zlmdb.Database) -> 'RealmStore':
        schema = RealmStore(db)

        schema._sessions = db.attach_table(Sessions)

        assert schema._sessions is not None

        schema._idx_sessions_by_session_id = db.attach_table(IndexSessionsBySessionId)
        schema._sessions.attach_index('idx1', schema._idx_sessions_by_session_id, lambda session:
                                      (session.session, session.joined_at))

        schema._publications = db.attach_table(Publications)
        schema._events = db.attach_table(Events)

        return schema
