from functools import wraps

from django.db import close_old_connections, reset_queries
from procrastinate.contrib.django import app as procrastinate_app


def plug_psycopg_leak(func):
    """https://github.com/procrastinate-org/procrastinate/issues/1316"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        close_old_connections()
        reset_queries()
        try:
            return func(*args, **kwargs)
        finally:
            close_old_connections()
            reset_queries()

    return wrapper


@procrastinate_app.task
@plug_psycopg_leak
def test_task(text):
    print(f"Procrastinate test task invoked: {text}")
