from schematics import Model
from schematics.types import ModelType, StringType, DateTimeType, ListType


class Resource(Model):
    resource_type = StringType(deserialize_from='ResourceType', serialize_when_none=False)
    resource_name = StringType(deserialize_from='ResourceName', serialize_when_none=False)


class Event(Model):
    event_id = StringType(deserialize_from='EventId', serialize_when_none=False)
    event_name = StringType(deserialize_from='EventName', serialize_when_none=False)
    read_only = StringType(deserialize_from='ReadOnly', serialize_when_none=False)
    access_key_id = StringType(deserialize_from='AccessKeyId', serialize_when_none=False)
    event_time = DateTimeType(deserialize_from='EventTime', serialize_when_none=False)
    event_source = StringType(deserialize_from='EventSource', serialize_when_none=False)
    username = StringType(deserialize_from='Username', serialize_when_none=False)
    resources = ListType(ModelType(Resource), deserialize_from='Resources', default=[])
    cloud_trail_event = StringType(deserialize_from='CloudTrailEvent', serialize_when_none=False)


class Log(Model):
    results = ListType(ModelType(Event), default=[])
