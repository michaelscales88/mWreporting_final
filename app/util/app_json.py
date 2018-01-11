# util/app_json.py
from datetime import datetime, timedelta
from dateutil import parser
from flask import json
from sqlalchemy.types import TypeDecorator, VARCHAR
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.ext.declarative import DeclarativeMeta

CONVERTERS = {
    '__datetime__': parser.parse
}


class AlchemyJSONEncoder(json.JSONEncoder):

    def default(self, obj):
        # ORM models
        if isinstance(obj.__class__, DeclarativeMeta):
            data = {}
            fields = obj.__json__() if hasattr(obj, '__json__') else dir(obj)
            for field in [f for f in fields if not f.startswith('_') and f not in ['metadata', 'query', 'query_class']]:
                value = obj.__getattribute__(field)
                try:
                    json.dumps(value)
                    data[field] = value
                except TypeError:
                    data[field] = None
            return data

        elif isinstance(obj, datetime):
            return {
                '__type__': 'datetime',
                'year': obj.year,
                'month': obj.month,
                'day': obj.day,
                'hour': obj.hour,
                'minute': obj.minute,
                'second': obj.second,
                'microsecond': obj.microsecond,
            }

        elif isinstance(obj, timedelta):
            return {
                '__type__': 'timedelta',
                'days': obj.days,
                'seconds': obj.seconds,
                'microseconds': obj.microseconds,
            }

        else:
            return json.JSONEncoder.default(self, obj)


class AlchemyJSONDecoder(json.JSONDecoder):
    """
    Converts a json string, where datetime and timedelta objects were converted
    into objects using the DateTimeAwareJSONEncoder, back into a python object.
    """

    def __init__(self):
        super().__init__(object_hook=self.dict_to_object)

    def dict_to_object(self, d):
        if '__type__' not in d:
            return d

        type = d.pop('__type__')
        if type == 'datetime':
            return datetime(**d)
        elif type == 'timedelta':
            return timedelta(**d)
        else:
            # Oops... better put this back together.
            d['__type__'] = type
            return d


# Encoder function
def my_dumps(obj):
    print('dumping')
    return json.dumps(obj, cls=AlchemyJSONEncoder)


# Decoder function
def my_loads(obj):
    print('loading')
    return json.loads(obj, cls=AlchemyJSONDecoder)


class JSONEncodedDict(TypeDecorator):
    """Represents an immutable structure as a json-encoded string.

    Usage::

        JSONEncodedDict(255)

    """

    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = my_dumps(value)

        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = my_loads(value)
        return value


class MutableDict(Mutable, dict):
    @classmethod
    def coerce(cls, key, value):
        """Convert plain dictionaries to MutableDict."""

        if not isinstance(value, MutableDict):

            if isinstance(value, dict):
                return MutableDict(value)

            # this call will raise ValueError
            return Mutable.coerce(key, value)
        else:
            return value

    def __setitem__(self, key, value):
        """Detect dictionary set events and emit change events."""

        dict.__setitem__(self, key, value)
        self.changed()

    def __delitem__(self, key):
        """Detect dictionary del events and emit change events."""

        dict.__delitem__(self, key)
        self.changed()


json_type = MutableDict.as_mutable(JSONEncodedDict)
