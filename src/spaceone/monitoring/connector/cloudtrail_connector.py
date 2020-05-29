# -*- coding: utf-8 -*-

import os
import os.path
# AWS SDK for Python
import boto3
import json
import re
import logging
import pprint
import time

from multiprocessing import Pool

from datetime import datetime
from spaceone.core.transaction import Transaction
from spaceone.core.error import *
from spaceone.core.connector import BaseConnector

from spaceone.monitoring.error import *

__all__ = ["CloudTrailConnector"]


_LOGGER = logging.getLogger(__name__)

RESOURCES = ['cloudformation', 'cloudwatch', 'dynamodb', 'ec2', 'glacier', 'iam', 'opsworks', 's3', 'sns', 'sqs']
DEFAULT_REGION = 'us-east-1'
NUMBER_OF_CONCURRENT = 4


class CloudTrailConnector(BaseConnector):

    def __init__(self, transaction, config):
        super().__init__(transaction, config)

    def create_session(self, options, secret_data):
        """ Verify CloudTrail Session
        """
        create_session(secret_data, options)

    def collect_info(self, query, secret_data, start, end, resource, sort, limit=200):
        """
        Args:
            query (dict): example
                  {
                      'instance_id': ['i-123', 'i-2222', ...]
                      'instance_type': 'm4.xlarge',
                      'region_name': ['aaaa']
                  }
            resource: arn:aws:ec2:<REGION>:<ACCOUNT_ID>:instance/<instance-id>
        If there is regiona_name in query, this indicates searching only these regions
        """
        (query, resource_ids, region_name) = self._check_query(query)
        post_filter_cache = False if len(region_name) > 0 else True

        try:
            (resource_ids, regions) = _parse_arn(resource)
            print(resource_ids)
            print(regions)
        except Exception as e:
            _LOGGER.error(f'[collect_info] fail to parse arn:{e}')

        params = []
        region_name_list = []               # For filter_cache
        for region in regions:
            params.append({
                'region_name': region,
                'query': query,
                'resource_ids': resource_ids,
                'secret_data': secret_data,
                'start': start,
                'end': end,
                'sort': sort,
                'limit': limit
            })

        with Pool(NUMBER_OF_CONCURRENT) as pool:

            result = pool.map(discover_cloudtrail, params)

            no_result = True
            for resources in result:
                (collected_resources, region_name) = resources
                if len(collected_resources) > 0:
                    region_name_list.append(region_name)
                    try:
                        response = _prepare_response_schema()
                        response['result'] = {'logs': collected_resources}
                        no_result = False
                        yield response
                    except Exception as e:
                        _LOGGER.error(f'[collect_info] skip return {resource}, {e}')
                else:
                    _LOGGER.debug(f'[collect_info] no collected_resources at {region_name}')
            if no_result:
                # return final data
                response = _prepare_response_schema()
                response['result'] = {'logs': []}
                yield response


    def _check_query(self, query):
        resource_ids = []
        filters = []
        region_name = []
        for key, value in query.items():
            if key == 'instance_id' and isinstance(value, list):
                resource_ids = value

            elif key == 'region_name' and isinstance(value, list):
                region_name.extend(value)

            else:
                if isinstance(value, list) == False:
                    value = [value]

                if len(value) > 0:
                    filters.append({'Name': key, 'Values': value})

        return (filters, resource_ids, region_name)

#######################
# AWS Boto3 session
#######################
def create_session(secret_data: dict, options={}):
    _check_secret_data(secret_data)

    aws_access_key_id = secret_data['aws_access_key_id']
    aws_secret_access_key = secret_data['aws_secret_access_key']
    role_arn = secret_data.get('role_arn')

    try:
        if role_arn:
            return _create_session_with_assume_role(aws_access_key_id, aws_secret_access_key, role_arn)
        else:
            return _create_session_with_access_key(aws_access_key_id, aws_secret_access_key)
    except Exception as e:
        raise ERROR_INVALID_CREDENTIALS()

def _check_secret_data(secret_data):
    if 'aws_access_key_id' not in secret_data:
        raise ERROR_REQUIRED_PARAMETER(key='secret.aws_access_key_id')

    if 'aws_secret_access_key' not in secret_data:
        raise ERROR_REQUIRED_PARAMETER(key='secret.aws_secret_access_key')

def _create_session_with_access_key(aws_access_key_id, aws_secret_access_key):
    session = boto3.Session(aws_access_key_id=aws_access_key_id,
                                 aws_secret_access_key=aws_secret_access_key)

    sts = session.client('sts')
    sts.get_caller_identity()
    return session

def _create_session_with_assume_role(aws_access_key_id, aws_secret_access_key, role_arn):
    _create_session_with_access_key(aws_access_key_id, aws_secret_access_key)

    sts = session.client('sts')
    assume_role_object = sts.assume_role(RoleArn=role_arn, RoleSessionName=utils.generate_id('AssumeRoleSession'))
    credentials = assume_role_object['Credentials']

    session = boto3.Session(aws_access_key_id=credentials['AccessKeyId'],
                            aws_secret_access_key=credentials['SecretAccessKey'],
                            aws_session_toke=credentials['SessionToken'])
    return session


def _set_connect(secret_data, region_name, service="cloudtrail"):
    """
    """
    session = create_session(secret_data)
    aws_conf = {}
    aws_conf['region_name'] = region_name

    if service in RESOURCES:
        resource = session.resource(service, **aws_conf)
        client = resource.meta.client
    else:
        resource = None
        client = session.client(service, region_name=region_name)
    return client, resource


def discover_cloudtrail(params):
    """
    Args: params (dict): {
                'region_name': 'str',
                'query': 'dict',
                'resource_ids': 'list'
                'secret_data': 'dict',
                'start': 'datetime',
                'end': 'datetime',
                'sort': 'dict',
                'limit': 'int'
            }

    Returns: Resources, region_name
    """
    print(f'[discover_cloudtrail] {params["region_name"]}')

    client, resource = _set_connect(params['secret_data'], params['region_name'])
    try:
        resources = _lookup_events(client, params)
        return resources
    except Exception as e:
        _LOGGER.error(f'[discover_cloudtrail] skip region: {params["region_name"]}, {e}')
    return [], params['region_name']


def _lookup_events(client, params):
    resource_list = []
    event_query = {}
    region_name = params['region_name']
    if 'resource_ids' in params:
        LookupAttributes = []
        resources = params['resource_ids']
        for resource in resources:
            LookupAttributes.append({'AttributeKey': 'Username', 'AttributeValue': resource})
        event_query.update({'LookupAttributes': LookupAttributes})

    event_query.update({'StartTime': params['start'],
                        'EndTime': params['end']
                        })
    # Paginator config
    limit = params.get('limit')
    print(f'limit: {limit}')
    page_size = limit if limit < 50 else 50
    event_query.update({'PaginationConfig': {'MaxItems': limit, 'PageSize': page_size}})
    try:
        print(event_query)
        paginator = client.get_paginator('lookup_events')
        response_iterator = paginator.paginate(**event_query)
        events = []
        for response in response_iterator:
            events.extend(response['Events'])
        if len(events) == 0:
            # Fast return if No resources
            print("No Event")
            return (events, region_name)

    except Exception as e:
        print(f'[_lookup_events] Fail to lookup CloudTrail events: {e}')
        return (resource_list, region_name)

    # Find Events
    for event in events:
        try:
            event_string = event["CloudTrailEvent"]
            detailed_event = _parse_cloud_trail_event(event_string)
            result = {'EventTime': event['EventTime'].isoformat(), 'AccessKeyId': event['AccessKeyId']}
            result.update(detailed_event)
            resource_list.append(result)

        except Exception as e:
            print(f'[_lookup_events] error {e}')
    return (resource_list, region_name)


def _parse_cloud_trail_event(cte):
    """ Parse CloudTrailEvent

    Args: CloudTrailEvent (raw data)
    Returns: dict
    """
    result = {}
    event = json.loads(cte)
    wanted_items = ['eventName', 'eventType', 'errorMessage']
    for item in wanted_items:
        if item in event:
            result[item] = event[item]
    print(f'parse cloud trail event: {result}')
    return result


def _parse_arn(arn):
    """
    ec2)  arn:aws:ec2:<REGION>:<ACCOUNT_ID>:instance/<instance-id>

    arn:partition:service:region:account-id:resource-id
    arn:partition:service:region:account-id:resource-type/resource-id
    arn:partition:service:region:account-id:resource-type:resource-id

    Returns: resource_list, [regions]
    """
    p = (r"(?P<arn>arn):"
         r"(?P<partition>aws|aws-cn|aws-us-gov):"
         r"(?P<service>[A-Za-z0-9_\-]*):"
         r"(?P<region>[A-Za-z0-9_\-]*):"
         r"(?P<account>[A-Za-z0-9_\-]*):"
         r"(?P<resources>[A-Za-z0-9_\-:/]*)")
    r = re.compile(p)
    match = r.match(arn)
    if match:
        d = match.groupdict()
    else:
        return (None, None)
    region = d.get('region', None)
    resource_id = None
    resources = d.get('resources', None)
    if resources:
        items = re.split('/|:', resources)
        if len(items) == 1:
            resource_id = items[0]
        elif len(items) == 2:
            resource_type = items[0]
            resource_id = items[1]
        else:
            print(f'ERROR parsing: {resources}')
    return [resource_id], [region]


def _prepare_response_schema() -> dict:
    return {
        'resource_type': 'monitoring.Log',
        'actions': [
            {
                'method': 'process'
            }],
        'result': {}
    }


if __name__ == "__main__":
    import os

    aki = os.environ.get('AWS_ACCESS_KEY_ID', "<YOUR_AWS_ACCESS_KEY_ID>")
    sak = os.environ.get('AWS_SECRET_ACCESS_KEY', "<YOUR_AWS_SECRET_ACCESS_KEY>")
    secret_data = {
        #        'region_name': 'ap-northeast-2',
        'aws_access_key_id': aki,
        'aws_secret_access_key': sak
    }
    conn = CloudTrailConnector(Transaction(), secret_data)
    #opts = conn.verify({}, secret_data)
    #print(opts)
    query = {}
    #query = {'region_name': ['ap-northeast-2', 'us-east-1']}
    #query = {}
    from datetime import datetime
    start = datetime(2020,4,9)
    end = datetime(2020,4,10)
    ec2_arn = 'arn:aws:ec2:ap-northeast-2:072548720675:instance/i-08c5592e084b24e20'
    sort = ""
    limit = 10
    resource_stream = conn.collect_info(query=query, secret_data=secret_data,
                                        start=start, end=end, resource=ec2_arn, sort=sort, limit=limit)
    for resource in resource_stream:
        print(resource)
