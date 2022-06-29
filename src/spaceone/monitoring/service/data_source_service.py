import logging
from spaceone.core.service import *
from spaceone.monitoring.manager.data_source_manager import DataSourceManager

_LOGGER = logging.getLogger(__name__)


@authentication_handler
@authorization_handler
@event_handler
class DataSourceService(BaseService):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_source_mgr: DataSourceManager = self.locator.get_manager('DataSourceManager')

    @check_required(['options'])
    def init(self, params):
        """ init plugin by options
        """
        return self.data_source_mgr.init(params)

    @transaction
    @check_required(['options', 'secret_data'])
    def verify(self, params):
        """ Verifying data source plugin

        Args:
            params (dict): {
                'schema': 'str',
                'options': 'dict',
                'secret_data': 'dict'
            }

        Returns:
            plugin_verify_response (dict)
        """
        self.data_source_mgr.verify(params)
