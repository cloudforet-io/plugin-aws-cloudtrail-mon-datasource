__all__ = ['PluginInfo']

from spaceone.api.monitoring.plugin import data_source_pb2
from spaceone.core.pygrpc.message_type import *


def PluginInfo(response):
    struct_response = change_struct_type(response)
    return data_source_pb2.PluginInfo(**struct_response)
