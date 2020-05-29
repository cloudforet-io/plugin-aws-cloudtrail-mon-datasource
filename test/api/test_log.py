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

    def test_valify(self):
        options = {}
        secret_data = {
            'aws_access_key_id': AKI,
            'aws_secret_access_key': SAK
        }
        resource_stream = self.monitoring.DataSource.verify({'options':options,
                                                             'secret_data':secret_data})
        for res in resource_stream:
            print_json(res)
 
    def test_list(self):
        options = {}
        secret_data = {
            'aws_access_key_id': AKI,
            'aws_secret_access_key': SAK
        }
        filter = {}
        resource = 'arn:aws:ec2:ap-northeast-2:072548720675:instance/i-08c5592e084b24e20'
        resource_stream = self.monitoring.Log.list({'options':options,
                                                    'secret_data':secret_data,
                                                    'filter':filter,
                                                    'resource': resource})
        print(resource_stream)

        for res in resource_stream:
            print_json(res)


if __name__ == "__main__":
    unittest.main(testRunner=RichTestRunner)
