from spaceone.core.error import *

class ERROR_PLUGIN_VERIFY_FAILED(ERROR_BASE):
    _message = '{plugin} failed to verify with {secret}'

class ERROR_INVALID_CREDENTIALS(ERROR_INVALID_ARGUMENT):
    _message = 'AWS credentials is invalid.'
