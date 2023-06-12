import copy
import logging
from spaceone.core.manager import BaseManager
from spaceone.monitoring.conf.monitoring_conf import *
from spaceone.monitoring.connector.cloudtrail_connector import CloudTrailConnector
from spaceone.monitoring.connector.ec2_connector import EC2Connector
from spaceone.monitoring.model.log_model import Log, Event

_LOGGER = logging.getLogger(__name__)


class MonitoringManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def list_logs(self, params):
        resource_type = params['query'].get('resource_type')
        keyword = params.get('keyword')

        for events in self.lookup_events(params):
            event_vos = self.set_events(events, keyword, resource_type)
            yield Log({'results': event_vos})

    def list_regions(self, params):
        ec2_connector: EC2Connector = self.locator.get_connector('EC2Connector', **params)
        ec2_connector.set_client('us-east-1')

        regions_info = ec2_connector.describe_regions()
        return [region_info.get('RegionName') for region_info in regions_info if region_info.get('RegionName')]

    def lookup_events(self, params):
        events = []

        region_name = params['query'].get('region_name', DEFAULT_REGION)
        resource_type = params['query'].get('resource_type')
        limit = params.get('limit', LIMIT)

        cloudtrail_connector: CloudTrailConnector = self.locator.get_connector('CloudTrailConnector', **params)
        cloudtrail_connector.set_client(region_name)

        if resource_type == 'AWS::IAM::AccessKey':
            events.extend(self.get_events_iam_access_key(params))
        else:
            for _events in cloudtrail_connector.lookup_events(params):
                events.extend(_events)

            if resource_type == 'AWS::IAM::User':
                events.extend(self.get_events_iam_user(params))

        event_chunk = []
        for event in events[:limit]:
            event_chunk.append(event)

            if len(event_chunk) == PAGINATOR_PAGE_SIZE:
                yield event_chunk
                event_chunk = []

        yield event_chunk

    def set_events(self, events, keyword, resource_type):
        event_vos = []
        for event in events:
            if keyword:
                if keyword.lower() not in event.get('EventName', '').lower():
                    continue

            if resource_type and resource_type != 'AWS::IAM::AccessKey':
                if filtered_event := self.filter_resource_type(event, resource_type):
                    event_vos.append(filtered_event)
            else:
                event_vos.append(Event(event, strict=False))

        return event_vos

    def get_events_iam_user(self, params):
        events = []

        cloudtrail_connector: CloudTrailConnector = self.locator.get_connector('CloudTrailConnector', **params)
        region_names = self.list_regions(params)

        console_login_target_user_name = ''
        _lookup_attr = params['query'].get('LookupAttributes')
        if _lookup_attr:
            console_login_target_user_name = _lookup_attr[0].get('AttributeValue')

        console_login_params = copy.deepcopy(params)
        console_login_params['query'] = {
            'LookupAttributes': [{'AttributeKey': 'EventName', 'AttributeValue': 'ConsoleLogin'}]}

        for region_name in region_names:
            cloudtrail_connector.set_client(region_name)
            for iam_user_events in cloudtrail_connector.lookup_events(console_login_params):
                for _user_event in iam_user_events:
                    if _user_event.get('Username') == console_login_target_user_name:
                        events.append(_user_event)

        return sorted(events, key=lambda event: event.get('EventTime'), reverse=True)

    def get_events_iam_access_key(self, params):
        events = []

        cloudtrail_connector: CloudTrailConnector = self.locator.get_connector('CloudTrailConnector', **params)
        region_names = self.list_regions(params)

        for region_name in region_names:
            cloudtrail_connector.set_client(region_name)
            for access_key_events in cloudtrail_connector.lookup_events(params):
                events.extend(access_key_events)
        return sorted(events, key=lambda event: event.get('EventTime'), reverse=True)

    @staticmethod
    def filter_resource_type(event, resource_type):
        if event['EventName'] in EXCLUDE_EVENT_NAME:
            return Event(event, strict=False)
        else:
            for resource in event.get('Resources', []):
                if resource.get('ResourceType') == resource_type:
                    return Event(event, strict=False)

        return None
