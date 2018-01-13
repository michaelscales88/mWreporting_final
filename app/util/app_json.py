# util/app_json.py
from datetime import datetime, timedelta
from flask import json
from sqlalchemy.types import TypeDecorator, VARCHAR
from sqlalchemy.ext.mutable import Mutable


class AlchemyJSONEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime):
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
            return super().default(obj)


class AlchemyJSONDecoder(json.JSONDecoder):
    """
    Converts a json string, where datetime and timedelta objects were converted
    into objects using the AlchemyJSONEncoder, back into a python object.
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


class JSONEncodedDict(TypeDecorator):
    """Represents an immutable structure as a json-encoded string.

    Usage::

        JSONEncodedDict(255)

    """
    impl = VARCHAR

    @property
    def python_type(self):
        pass

    def process_literal_param(self, value, dialect):
        pass

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value, cls=AlchemyJSONEncoder)

        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value, cls=AlchemyJSONDecoder)
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


def strfdelta(tdelta, fmt):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return fmt.format(**d)


class AppJSONEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, datetime):
            return o.strftime("%B %m %Y %X")
        elif isinstance(o, timedelta):
            return strfdelta(o, "{hours}:{minutes}:{seconds}")
        else:
            return o
