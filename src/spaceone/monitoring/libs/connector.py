from boto3.session import Session
from spaceone.core import utils
from spaceone.core.connector import BaseConnector
from spaceone.monitoring.conf.monitoring_conf import *

PAGINATOR_MAX_ITEMS = 10000
PAGINATOR_PAGE_SIZE = 50
DEFAULT_REGION = 'us-east-1'


class AWSConnector(BaseConnector):
    service = 'cloudtrail'
    secret_data = None
    session = None
    client = None
    schema = None

    def __init__(self, **kwargs):
        """
        kwargs
            - schema
            - options
            - secret_data
        """

        super().__init__(transaction=None, config=None)
        self.secret_data = kwargs.get('secret_data')
        self.schema = kwargs.get('schema', DEFAULT_SCHEMA)

    def verify(self, **kwargs):
        self.set_session(**kwargs)

    def set_session(self, region_name=DEFAULT_REGION):
        self.session = Session(aws_access_key_id=self.secret_data['aws_access_key_id'],
                               aws_secret_access_key=self.secret_data['aws_secret_access_key'],
                               region_name=region_name)

        # ASSUME ROLE
        if self.schema == 'aws_assume_role':
            role_arn = self.secret_data.get('role_arn')
            sts = self.session.client('sts')
            assume_role_object = sts.assume_role(RoleArn=role_arn,
                                                 RoleSessionName=utils.generate_id('AssumeRoleSession'))
            credentials = assume_role_object['Credentials']

            self.session = Session(aws_access_key_id=credentials['AccessKeyId'],
                                   aws_secret_access_key=credentials['SecretAccessKey'],
                                   region_name=region_name,
                                   aws_session_token=credentials['SessionToken'])

    def set_client(self, region_name=DEFAULT_REGION):
        self.set_session(region_name)
        self.client = self.session.client(self.service)

    @staticmethod
    def generate_query(is_paginate=False, **query):
        if is_paginate:
            query.update({
                'PaginationConfig': {
                    'MaxItems': PAGINATOR_MAX_ITEMS,
                    'PageSize': PAGINATOR_PAGE_SIZE,
                }
            })

        return query
