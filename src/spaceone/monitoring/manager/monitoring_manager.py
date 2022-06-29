import logging
from spaceone.core.manager import BaseManager
from spaceone.monitoring.conf.monitoring_conf import *
from spaceone.monitoring.connector.cloudtrail_connector import CloudTrailConnector
from spaceone.monitoring.model.log_model import Log, Event

_LOGGER = logging.getLogger(__name__)

class MonitoringManager(BaseManager):
    def __init__(self, transaction):
        super().__init__(transaction)

    def list_logs(self, params):
        cloudtrail_connector: CloudTrailConnector = self.locator.get_connector('CloudTrailConnector', **params)

        region_name = params['query'].get('region_name', DEFAULT_REGION)
        cloudtrail_connector.set_client(region_name)

        for events in cloudtrail_connector.lookup_events(params):
            yield Log({'logs': [Event(event, strict=False) for event in events]})

