import functools

from spaceone.api.core.v1 import plugin_pb2
from spaceone.api.monitoring.plugin import log_pb2
from spaceone.core.pygrpc.message_type import *

__all__ = ['LogsDataInfo']


def PluginAction(action_data):
    info = {
        'method': action_data['method'],
    }
    if 'options' in action_data:
        info.update({'options': change_struct_type(action_data['options'])})
    return plugin_pb2.PluginAction(**info)


def LogsDataInfo(result):
    info = {'logs': change_list_value_type(result['logs'])}
    return log_pb2.LogsDataInfo(**info)