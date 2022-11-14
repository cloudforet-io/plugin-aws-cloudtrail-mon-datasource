import logging
from spaceone.core.utils import load_json
from spaceone.monitoring.libs.connector import AWSConnector
from spaceone.monitoring.conf.monitoring_conf import *


_LOGGER = logging.getLogger(__name__)


class CloudTrailConnector(AWSConnector):
    service = 'cloudtrail'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def lookup_events(self, params):
        query = params['query']
        start = params['start']
        end = params['end']
        limit = params.get('limit', LIMIT)   # Force throttling because too many events cause performance issues

        lookup_attributes = query.get('LookupAttributes', [])

        paginator = self.client.get_paginator('lookup_events')

        _query = {
            'LookupAttributes': lookup_attributes,
            'StartTime': start,
            'EndTime': end
        }

        query = self.generate_query(is_paginate=True, limit=limit, **_query)
        response_iterator = paginator.paginate(**query)

        for response in response_iterator:
            events = response.get('Events', [])

            for event in events:
                if 'CloudTrailEvent' in event:
                    cloud_trail_event = load_json(event['CloudTrailEvent'])
                    event['CloudTrailEvent'] = cloud_trail_event

            yield events
