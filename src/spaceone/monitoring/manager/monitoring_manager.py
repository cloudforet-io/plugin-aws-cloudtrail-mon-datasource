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
        resource_type = params['query'].get('resource_type')
        keyword = params.get('keyword')
        cloudtrail_connector.set_client(region_name)

        for events in cloudtrail_connector.lookup_events(params):
            event_vos = self.set_events(events, keyword, resource_type)
            yield Log({'logs': event_vos})

    def set_events(self, events, keyword, resource_type):
        event_vos = []
        for event in events:
            if keyword:
                if keyword.lower() not in event.get('EventName', '').lower():
                    continue

            if resource_type:
                event_vos.extend(self.filter_resource_type(event, resource_type))
            else:
                event_vos.append(Event(event, strict=False))

        return event_vos

    @staticmethod
    def filter_resource_type(event, resource_type):
        event_vos = []
        for resource in event.get('Resources', []):
            if resource.get('ResourceType') == resource_type:
                event_vos.append(Event(event, strict=False))
                break

        return event_vos
