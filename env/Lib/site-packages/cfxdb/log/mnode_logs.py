##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################

from zlmdb import table, MapTimestampUuidFlatBuffers

from cfxdb.log.mnode_log import MNodeLog


@table('256a071f-5aeb-47f3-8786-97cd8281bdb7', build=MNodeLog.build, cast=MNodeLog.cast)
class MNodeLogs(MapTimestampUuidFlatBuffers):
    """
    Managed node heartbeat log records (``(timestamp, node_id) -> node_log``).
    """
