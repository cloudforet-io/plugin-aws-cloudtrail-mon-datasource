# -*- coding: utf-8 -*-
import logging

from spaceone.api.monitoring.plugin import log_pb2, log_pb2_grpc
from spaceone.core.pygrpc import BaseAPI
from spaceone.core.pygrpc.message_type import *

_LOGGER = logging.getLogger(__name__)

class Log(BaseAPI, log_pb2_grpc.LogServicer):

    pb2 = log_pb2
    pb2_grpc = log_pb2_grpc

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('MonitoringService', metadata) as log_svc:
            resource_stream = log_svc.list_resources(params)
            for resource in resource_stream:
                result = resource.get('result')
                # res = {
                #     'resource_type': (resource['resource_type']),
                #     'actions': resource['actions'],
                #     'result': resource['result']
                #
                # }
                _LOGGER.debug(f'[list] LogsDataInfo: {result}')
                yield self.locator.get_info('LogsDataInfo', result)
