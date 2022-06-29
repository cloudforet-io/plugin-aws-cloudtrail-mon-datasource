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
            'query': {
                'region_name': 'ap-northeast-2',
                'LookupAttributes': [
                    {'AttributeKey': 'ResourceName', 'AttributeValue': 'i-03073d34be471a2cb'}
                ]
            },
            'start': '2022-03-20 21:40:43.789618',
            'end': '2022-06-28 21:40:21.661581'
        }

        resource_stream = self.monitoring.Log.list(params)

        for res in resource_stream:
            print_json(res)


if __name__ == "__main__":
    unittest.main(testRunner=RichTestRunner)
