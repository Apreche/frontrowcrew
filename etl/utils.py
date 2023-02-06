import os
import requests
import tempfile
from http import HTTPStatus
from urllib.parse import urljoin
from django.core.files.storage import default_storage


def download_to_default_storage(old_path: str, new_base_path: str) -> None:
    """ Download file at old_path and upload to default storage at new path"""
    BASE_URL = "https://frontrowcrew.com/media/"
    full_url = urljoin(BASE_URL, old_path)
    response = requests.get(full_url, allow_redirects=True)
    with tempfile.TemporaryFile() as local_file:
        local_file.write(response.content)
        destination_path = os.path.join(
            new_base_path,
            os.path.basename(old_path)
        )
        default_storage.save(destination_path, local_file)
