import logging
from spaceone.core.utils import load_json
from spaceone.monitoring.libs.connector import AWSConnector

_LOGGER = logging.getLogger(__name__)


class EC2Connector(AWSConnector):
    service = 'ec2'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def describe_regions(self):
        response = self.client.describe_regions()
        return response.get('Regions', [])
