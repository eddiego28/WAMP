##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################

from zlmdb import table, MapTimestampUuidStringFlatBuffers

from cfxdb.log.mworker_log import MWorkerLog


@table('5ceaa500-4832-451c-adf4-4fc4968cece0', build=MWorkerLog.build, cast=MWorkerLog.cast)
class MWorkerLogs(MapTimestampUuidStringFlatBuffers):
    """
    Managed node worker heartbeat log records (``(timestamp, node_id, worker_id) -> worker_log``).
    """
