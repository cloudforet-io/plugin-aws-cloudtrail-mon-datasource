import logging

from spaceone.core.manager import BaseManager
from spaceone.monitoring.connector.cloudtrail_connector import CloudTrailConnector

_LOGGER = logging.getLogger(__name__)


class AWSManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aws_connector = self.locator.get_connector('CloudTrailConnector')

    def verify(self, options, secret_data):
        self.aws_connector.create_session(options, secret_data)

