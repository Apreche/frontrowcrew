# Set the correct length on every podcast enclosure

import os
import requests
import sqlite3
import tqdm


from django.conf import settings

from podcasts import models as podcast_models


class ContentLengthGetter:
    DB_FILE_PATH = "etl/data/content_length.db"

    def __init__(self):
        full_file_path = os.path.join(
            settings.BASE_DIR, self.DB_FILE_PATH
        )
        self.db = sqlite3.connect(full_file_path)
        self.cursor = self.db.cursor()

    def __del__(self):
        self.db.close()

    def _get_length_from_db(self, url):
        """ If we already have the length in the sqlite db, use it """
        query = "SELECT length from content_length where url = ?"
        result = self.cursor.execute(query, (url,))
        row = result.fetchone()
        if row is not None:
            length, *_ = row
            return int(length)
        return None

    def _get_length_from_web(self, url):
        """ If we don't have the length, get it from the web and put it in the db """
        response = requests.head(
            url,
            allow_redirects=True,
        )
        content_length = response.headers.get("Content-Length", None)
        if content_length.isnumeric():
            query = "INSERT INTO content_length (url, length) VALUES (?, ?)"
            self.cursor.execute(query, (url, content_length))
            self.db.commit()
            return int(content_length)
        else:
            return None

    def get_length(self, url):
        """ Get the content length of a particular url """
        db_length = self._get_length_from_db(url)
        if db_length is None:
            return self._get_length_from_web(url)
        return db_length


def run() -> None:
    enclosures = podcast_models.PodcastEnclosure.objects.all()
    length_getter = ContentLengthGetter()

    for enclosure in tqdm.tqdm(enclosures, desc="Enclosure Content Lengths"):
        url = enclosure.url
        content_length = length_getter.get_length(url)
        if content_length is not None:
            enclosure.length = content_length
            enclosure.save()
