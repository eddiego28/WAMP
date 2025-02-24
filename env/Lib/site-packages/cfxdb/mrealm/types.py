##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################

from cfxdb.gen.mrealm.WorkerGroupStatus import WorkerGroupStatus

STATUS_BY_CODE = {
    WorkerGroupStatus.NONE: 'NONE',
    WorkerGroupStatus.STOPPED: 'STOPPED',
    WorkerGroupStatus.STARTING: 'STARTING',
    WorkerGroupStatus.RUNNING: 'RUNNING',
    WorkerGroupStatus.PAUSED: 'PAUSED',
    WorkerGroupStatus.STOPPING: 'STOPPING',
    WorkerGroupStatus.ERROR: 'ERROR',
    WorkerGroupStatus.DEGRADED: 'DEGRADED',
}
STATUS_BY_NAME = {
    'NONE': WorkerGroupStatus.NONE,
    'STOPPED': WorkerGroupStatus.STOPPED,
    'STARTING': WorkerGroupStatus.STARTING,
    'RUNNING': WorkerGroupStatus.RUNNING,
    'PAUSED': WorkerGroupStatus.PAUSED,
    'STOPPING': WorkerGroupStatus.STOPPING,
    'ERROR': WorkerGroupStatus.ERROR,
    'DEGRADED': WorkerGroupStatus.DEGRADED,
}
STATUS_STOPPED = WorkerGroupStatus.STOPPED
STATUS_STARTING = WorkerGroupStatus.STARTING
STATUS_RUNNING = WorkerGroupStatus.RUNNING
STATUS_PAUSED = WorkerGroupStatus.PAUSED
STATUS_STOPPING = WorkerGroupStatus.STOPPING
STATUS_ERROR = WorkerGroupStatus.ERROR
STATUS_DEGRADED = WorkerGroupStatus.DEGRADED
