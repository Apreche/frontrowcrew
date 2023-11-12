"""global utils for frontrowcrew"""
import http
import uuid

from django.http import response

from . import forms


def str_to_bool(input_string: str) -> bool:
    """check string for truthiness"""
    truthy_strings = ["true", "tru", "t", "y", "yes", "1"]
    return input_string.lower() in truthy_strings


def uuid4_str() -> str:
    """Generate a uuid4 as a string"""
    return str(uuid.uuid4())


def compress_whitespace(input_string: str) -> str:
    """
    Take a string and break it up into lines
    Remove all lines which are entirely whitespace
    Remove all leading and trailing whitespace from each line
    Join all lines back together with no separation

    NOTE: Useful for taking human readable HTML and embedding it in e.g: RSS
    """
    return "".join(
        [
            line.strip()
            for line in input_string.splitlines()
            if line and not line.isspace()
        ]
    )


class HttpResponseSeeOther(response.HttpResponseRedirectBase):
    """HTTPResponse for use on forms submission redirects"""

    status_code = http.HTTPStatus.SEE_OTHER.value


__all__ = [
    "HttpResponseSeeOther",
    "forms",
    "str_to_bool",
]
