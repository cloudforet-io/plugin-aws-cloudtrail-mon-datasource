# -*- coding: utf-8 -*-

__all__ = ['MonitoringManager']

import logging

from datetime import datetime

from spaceone.core import config
from spaceone.core.error import *
from spaceone.core.manager import BaseManager
import boto3

_LOGGER = logging.getLogger(__name__)

class MonitoringManager(BaseManager):
    def __init__(self, transaction):
        super().__init__(transaction)

    def list_resources(self, options, secret_data, filters, resource, start, end, sort, limit):
        # call ec2 connector

        connector = self.locator.get_connector('CloudTrailConnector')

        # make query, based on options, secret_data, filter
        query = filters

        return connector.collect_info(query, secret_data, start, end, resource, sort, limit)
