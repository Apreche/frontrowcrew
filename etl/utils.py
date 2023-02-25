import os
import requests
import tempfile
from http import HTTPStatus
from urllib.parse import urljoin
from django.core.files.storage import default_storage


def download_to_default_storage(
    old_path: str,
    new_filename: str = "",
    old_base_url: str = "https://frontrowcrew.com/media/",
    new_base_path: str = "/",
) -> None:
    """ Download file at old_path and upload to default storage at new path"""

    full_old_url = urljoin(old_base_url, old_path)
    response = requests.get(full_old_url, allow_redirects=True)

    with tempfile.TemporaryFile() as local_file:
        local_file.write(response.content)

        new_filename = new_filename or os.path.basename(old_path)

        destination_path = os.path.join(
            new_base_path, new_filename
        )
        filename = default_storage.save(destination_path, local_file)
    return filename


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]
