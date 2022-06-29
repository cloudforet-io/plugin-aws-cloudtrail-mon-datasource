import logging
from spaceone.core.manager import BaseManager
from spaceone.monitoring.connector.cloudtrail_connector import CloudTrailConnector
from spaceone.monitoring.model.data_source_response_model import DataSourceMetadata
from spaceone.monitoring.model.metadata.metadata import LogMetadata
from spaceone.monitoring.model.metadata.metadata_dynamic_field import TextDyField, DateTimeDyField, ListDyField
from spaceone.monitoring.conf.monitoring_conf import *

_LOGGER = logging.getLogger(__name__)


class DataSourceManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def init(params):
        options = params['options']

        metadata = LogMetadata.set_meta(
            fields=[
                TextDyField.data_source('Event Name', 'event_name'),
                DateTimeDyField.data_source('Event Time', 'event_time'),
                TextDyField.data_source('User Name', 'username'),
                TextDyField.data_source('Event Source', 'event_source'),
                ListDyField.data_source('Resource Type', 'resources', options={
                    'sub_key': 'resource_type',
                    'delimiter': ', '
                }),
            ]
        )

        response_model = DataSourceMetadata({'_metadata': metadata})
        response_model.validate()
        return response_model.to_primitive()

    def verify(self, params):
        cloudtrail_connector: CloudTrailConnector = self.locator.get_connector('CloudTrailConnector', **params)
        cloudtrail_connector.set_client(DEFAULT_REGION)
