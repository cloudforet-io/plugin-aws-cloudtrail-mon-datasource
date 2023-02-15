import os
import unittest
from spaceone.core.unittest.runner import RichTestRunner
from spaceone.tester import TestCase, print_json

AKI = os.environ.get('AWS_ACCESS_KEY_ID', None)
SAK = os.environ.get('AWS_SECRET_ACCESS_KEY', None)

if AKI == None or SAK == None:
    print("""
##################################################
# ERROR 
#
# Configure your AWS credential first for test
##################################################
example)

export AWS_ACCESS_KEY_ID=<YOUR_AWS_ACCESS_KEY_ID>
export AWS_SECRET_ACCESS_KEY=<YOUR_AWS_SECRET_ACCESS_KEY>

""")
    exit

class TestLog(TestCase):

    def test_init(self):
        v_info = self.monitoring.DataSource.init({'options': {}})
        print_json(v_info)

    def test_verify(self):
        schema = 'aws_access_key'
        options = {
        }
        secret_data = {
            'aws_access_key_id': AKI,
            'aws_secret_access_key': SAK
        }
        self.monitoring.DataSource.verify({'schema': schema, 'options': options, 'secret_data': secret_data})

    def test_log_list(self):
        secret_data = {
            'aws_access_key_id': AKI,
            'aws_secret_access_key': SAK
        }

        params = {
            'options': {},
            'secret_data': secret_data,
            'schema': 'aws_access_key',
            # 'keyword': 'Create',
            # 'query': {
            #     'region_name': 'us-east-1',
            #     'LookupAttributes': [
            #         {'AttributeKey': 'ResourceName', 'AttributeValue': 'jihyung.song'}
            #     ],
            #     'resource_type': 'AWS::IAM::User'
            # },
            'query': {
                'region_name': 'ap-northeast-2',
                'LookupAttributes': [
                    {'AttributeKey': 'ResourceName', 'AttributeValue': 'i-01ee7c46efad30111'}
                ],
                'resource_type': 'AWS::EC2::Instance'
            },
            # 'query': {
            #     'LookupAttributes': [
            #         {'AttributeKey': 'AccessKeyId', 'AttributeValue': 'AKIATYAD7BLQE4XLKUFT'}
            #     ],
            #     'resource_type': 'AWS::IAM::AccessKey',
            #     'region_name': 'us-east-1'
            # },
            'start': '2022-11-12T11:15:12.717Z',
            'end': '2022-11-14T11:15:12.717Z'
        }

        resource_stream = self.monitoring.Log.list(params)

        for res in resource_stream:
            print_json(res)


if __name__ == "__main__":
    unittest.main(testRunner=RichTestRunner)
