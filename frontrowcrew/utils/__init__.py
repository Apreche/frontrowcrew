"""global utils for frontrowcrew"""
import uuid
import http
from django.http import response

from . import forms


def str_to_bool(input_string: str) -> bool:
    """ check string for truthiness """
    truthy_strings = ["true", "tru", "t", "y", "yes", "1"]
    return input_string.lower() in truthy_strings


def uuid4_str() -> str:
    """ Generate a uuid4 as a string """
    return str(uuid.uuid4())


class HttpResponseSeeOther(response.HttpResponseRedirectBase):
    """ HTTPResponse for use on forms submission redirects """
    status_code = http.HTTPStatus.SEE_OTHER.value


__all__ = [
    "HttpResponseSeeOther",
    "forms",
    "str_to_bool",
]
