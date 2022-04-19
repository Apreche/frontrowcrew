
from http import HTTPStatus


def skip_if_invalid_rss_xml(f):
    """
    Decorator to skip a test if the setup response failed
    """
    def wrapper(self, *args, **kwargs):
        if self.response.status_code != HTTPStatus.OK:
            self.skipTest("Skip because of failed request.")
        etree = getattr(self, "etree", None)
        etree_exception = getattr(self, "etree_exception", None)
        if (etree is None) or (etree_exception is not None):
            self.skipTest("Skip test because RSS XML is invalid.")
        return f(self, *args, **kwargs)
    return wrapper
