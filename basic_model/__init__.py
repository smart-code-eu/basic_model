#
# Modifications Copyright (C) 2019 SMART CODE, razvoj aplikacij, d.o.o.
#
# Copyright 2016 SmartBear Software
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at [apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Original code:
# https://github.com/swagger-api/swagger-codegen/blob/master/modules/swagger-codegen/src/main/resources/flaskConnexion/model.mustache
#

import datetime
import importlib
import pprint
import re

import typing
from typing import ForwardRef

import six

T = typing.TypeVar('T')


def _deserialize(data, klass, models_module=None):
    """Deserializes dict, list, str into an object.

    :param data: dict, list or str.
    :param klass: class literal, or string of class name.

    :return: object.
    """
    if data is None:
        return None

    if klass in six.integer_types or klass in (float, str, bool):
        return _deserialize_primitive(data, klass)
    elif klass == object:
        return _deserialize_object(data)
    elif klass == datetime.date:
        return deserialize_date(data)
    elif klass == datetime.datetime:
        return deserialize_datetime(data)
    elif hasattr(klass, '__origin__'):
        if klass.__origin__ == list:
            return _deserialize_list(data, klass.__args__[0], models_module)
        if klass.__origin__ == dict:
            return _deserialize_dict(data, klass.__args__[1], models_module)
    else:
        return deserialize_model(data, klass, models_module)


def _deserialize_primitive(data, klass):
    """Deserializes to primitive type.

    :param data: data to deserialize.
    :param klass: class literal.

    :return: int, long, float, str, bool.
    :rtype: int | long | float | str | bool
    """
    try:
        value = klass(data)
    except UnicodeEncodeError:
        value = six.u(data)
    except TypeError:
        value = data
    return value


def _deserialize_object(value):
    """Return a original value.

    :return: object.
    """
    return value


def deserialize_date(string):
    """Deserializes string to date.

    :param string: str.
    :type string: str
    :return: date.
    :rtype: date
    """
    try:
        from dateutil.parser import parse
        return parse(string).date()
    except ImportError:
        return string


def deserialize_datetime(string):
    """Deserializes string to datetime.

    The string should be in iso8601 datetime format.

    :param string: str.
    :type string: str
    :return: datetime.
    :rtype: datetime
    """
    try:
        from dateutil.parser import parse
        return parse(string)
    except ImportError:
        return string


def convert_camel_case_to_snake_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def deserialize_model(data, klass, models_module=None):
    """Deserializes list or dict to model.

    :param data: dict, list.
    :type data: dict | list
    :param klass: class literal.
    :return: model object.
    """
    if isinstance(klass, str):
        resolved = getattr(importlib.import_module("{0}.{1}".format(models_module, convert_camel_case_to_snake_case(klass))), klass)
    elif isinstance(klass, ForwardRef):
        print(klass)
        klass = klass.__forward_arg__
        print(klass)
        module_name = "{0}.{1}".format(models_module, convert_camel_case_to_snake_case(klass))
        class_name = klass
        print(module_name)
        resolved = getattr(importlib.import_module(module_name), class_name)
    else:
        print("Resolving using string: {0}".format(klass))
        resolved = klass

    instance = resolved()

    if not instance.attr_types:
        return data

    for attr, attr_type in six.iteritems(instance.  attr_types):
        real_attr = instance.attr_map[attr]

        if data is not None \
                and attr in data \
                and isinstance(data, (list, dict)):
            value = data[attr]
            setattr(instance, real_attr, _deserialize(value, attr_type, models_module))

    return instance


def _deserialize_list(data, boxed_type, models_module=None):
    """Deserializes a list and its elements.

    :param data: list to deserialize.
    :type data: list
    :param boxed_type: class literal.

    :return: deserialized list.
    :rtype: list
    """
    return [_deserialize(sub_data, boxed_type, models_module)
            for sub_data in data]


def _deserialize_dict(data, boxed_type, models_module=None):
    """Deserializes a dict and its elements.

    :param data: dict to deserialize.
    :type data: dict
    :param boxed_type: class literal.

    :return: deserialized dict.
    :rtype: dict
    """
    return {k: _deserialize(v, boxed_type, models_module)
            for k, v in six.iteritems(data)}


class Model(object):
    # swaggerTypes: The key is attribute name and the
    # value is attribute type.
    attr_types = {}

    # attributeMap: The key is attribute name and the
    # value is json key in definition.
    attr_map = {}

    def __init__(self):
        pass

    @classmethod
    def from_dict(cls: typing.Type[T], dikt, models_module=None) -> T:
        """Returns the dict as a model"""
        return deserialize_model(dikt, cls, models_module)

    def to_dict(self):
        """Returns the model properties as a dict

        :rtype: dict
        """
        result = {}

        for attr, _ in six.iteritems(self.attr_types):
            correct_attr = self.attr_map[attr]
            value = getattr(self, correct_attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model

        :rtype: str
        """
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other

    def __hash__(self):
        return hash(self.id)