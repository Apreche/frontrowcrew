"""global utils for betafrontrowcrew"""
import http
from django.http import response

from . import forms

__all__ = [
    "HTTPResponseSeeOther",
    "default_base_url",
    "forms",
    "str_to_bool",
]


def str_to_bool(input_string: str) -> bool:
    """ check string for truthiness """
    truthy_strings = ["true", "tru", "t", "y", "yes", "1"]
    return input_string.lower() in truthy_strings


class HttpResponseSeeOther(response.HttpResponseRedirectBase):
    """ HTTPResponse for use on forms submission redirects """
    status_code = http.HTTPStatus.SEE_OTHER.value
