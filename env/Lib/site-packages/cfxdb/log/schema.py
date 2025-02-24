##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################

from cfxdb.log.mnode_logs import MNodeLogs
from cfxdb.log.mworker_logs import MWorkerLogs


class Schema(object):
    def __init__(self, db):
        self.db = db

    # mnode_logs: MNodeLogs
    mnode_logs = None
    """
    Managed node log records.
    """

    # mworker_logs: MWorkerLogs
    mworker_logs = None
    """
    Managed node worker log records.
    """

    @staticmethod
    def attach(db):
        """
        Factory to create a schema from attaching to a database. The schema tables
        will be automatically mapped as persistant maps and attached to the
        database slots.

        :param db: zlmdb.Database
        :return: object of Schema
        """
        schema = Schema(db)

        schema.mnode_logs = db.attach_table(MNodeLogs)
        schema.mworker_logs = db.attach_table(MWorkerLogs)

        return schema
