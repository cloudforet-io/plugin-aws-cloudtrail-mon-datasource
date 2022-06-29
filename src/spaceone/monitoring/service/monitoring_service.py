import logging
from spaceone.core.service import *

_LOGGER = logging.getLogger(__name__)


@authentication_handler
class MonitoringService(BaseService):
    def __init__(self, metadata):
        super().__init__(metadata)

    @transaction
    @check_required(['options', 'secret_data', 'query', 'start', 'end'])
    @change_timestamp_value(['start', 'end'], timestamp_format='iso8601')
    def list_logs(self, params):
        """ Get quick list of resources

        Args:
            params (dict) {
                'options': 'dict',
                'schema': 'str',
                'secret_data': 'dict',
                'filter': 'dict',
                'resource': 'str',
                'start': 'timestamp',
                'end': 'timestamp',
                'sort': 'dict',
                'limit': 'int'
            }

        Returns: list of resources
        """
        mon_manager = self.locator.get_manager('MonitoringManager')
        for logs in mon_manager.list_logs(params):
            yield logs
