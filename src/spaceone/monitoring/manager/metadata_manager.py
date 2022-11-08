import logging
from spaceone.core.manager import BaseManager
from spaceone.monitoring.model.metadata.metadata import LogMetadata
from spaceone.monitoring.model.metadata.metadata_dynamic_field import TextDyField, DateTimeDyField, ListDyField, \
    MoreField

_LOGGER = logging.getLogger(__name__)


class MetadataManager(BaseManager):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def get_data_source_metadata():
        metadata = LogMetadata.set_fields(
            name='cloudtrail-table',
            fields=[
                MoreField.data_source('Event Name', 'event_name', options={
                    'layout': {
                        'name': 'Event Details',
                        'type': 'popup',
                        'options': {
                            'layout': {
                                'type': 'raw'
                            }
                        }
                    }
                }),
                TextDyField.data_source('User Name', 'username'),
                DateTimeDyField.data_source('Event Time', 'event_time'),
                TextDyField.data_source('Access Key ID', 'access_key_id'),
                TextDyField.data_source('Region', 'cloud_trail_event.awsRegion'),
                TextDyField.data_source('Error Message', 'cloud_trail_event.errorMessage')
            ]
        )
        return metadata
