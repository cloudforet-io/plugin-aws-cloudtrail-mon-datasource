__all__ = ['LogsDataInfo']

from spaceone.api.monitoring.plugin import log_pb2
from spaceone.core.pygrpc.message_type import *


def LogsDataInfo(result):
    logs_info = result.to_primitive()
    events = logs_info.get('results', [])
    results = {'results': [change_struct_type(event) for event in events]}
    return log_pb2.LogsDataInfo(**results)
