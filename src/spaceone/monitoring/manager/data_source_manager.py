import logging
from spaceone.core.manager import BaseManager
from spaceone.monitoring.connector.cloudtrail_connector import CloudTrailConnector
from spaceone.monitoring.model.data_source_response_model import DataSourceMetadata
from spaceone.monitoring.manager.metadata_manager import MetadataManager
from spaceone.monitoring.conf.monitoring_conf import *

_LOGGER = logging.getLogger(__name__)


class DataSourceManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def init(params):
        options = params['options']
        meta_manager = MetadataManager()
        response_model = DataSourceMetadata({'_metadata': meta_manager.get_data_source_metadata()}, strict=False)
        return response_model.to_primitive()

    def verify(self, params):
        cloudtrail_connector: CloudTrailConnector = self.locator.get_connector('CloudTrailConnector', **params)
        cloudtrail_connector.set_client(DEFAULT_REGION)
