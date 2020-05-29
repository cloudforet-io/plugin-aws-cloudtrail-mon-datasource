import logging

from spaceone.core.service import *

from spaceone.monitoring.error import *
from spaceone.monitoring.manager.aws_manager import AWSManager
from spaceone.monitoring.manager.data_source_manager import DataSourceManager

_LOGGER = logging.getLogger(__name__)


@authentication_handler
@authorization_handler
@event_handler
class DataSourceService(BaseService):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aws_mgr: AWSManager = self.locator.get_manager('AWSManager')
        self.data_source_mgr: DataSourceManager = self.locator.get_manager('DataSourceManager')

    @transaction
    @check_required(['options', 'secret_data'])
    def verify(self, params):
        """Plugin verify

        Args:
            params (dict): {
                'options': 'dict',
                'secret_data': 'dict'
            }

        Returns:
            plugin_response (dict)
        """

        self.aws_mgr.verify(params['options'], params['secret_data'])
        return self.data_source_mgr.make_response()
