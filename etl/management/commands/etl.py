import tqdm
import typing
import os
import sqlite3

from django.apps import apps as django_apps
from django.conf import settings
from django.core import management as django_management
from django.core.management.base import BaseCommand
from django.db import connection as django_db_connection
from django.db import models as django_models

from betafrontrowcrew.utils import db as db_utils
from etl import py_steps
from etl import utils as etl_utils


class Command(BaseCommand):
    help = "ETL from SQLite export of the old frontrowcrew.com database"

    ETL_STEPS_DIR = "etl/sql_steps"
    ETL_DB_FILE = "etl/data/frc_old.db"

    def _get_sqlite_file_path(self, *args, **kwargs) -> str:
        """ Get the absolute path of the sqlite file to ETL from """
        file_path = os.path.join(
            settings.BASE_DIR, self.ETL_DB_FILE
        )
        return os.path.abspath(file_path)

    def _execute_sqlite_file(
        self,
        *args,
        filename: str,
        sql_params: typing.List[typing.Union[str, int]] = [],
        **kwargs
    ) -> None:
        """ Execute an SQL file on the SQLite source database directly """
        sqlite_path = self._get_sqlite_file_path()
        sql_file_path = os.path.join(
            settings.BASE_DIR, self.ETL_STEPS_DIR, filename
        )
        with open(sql_file_path, "r") as sql_file:
            sql = sql_file.read()

        db = sqlite3.connect(sqlite_path)
        cursor = db.cursor()
        cursor.executescript(sql)
        db.commit()
        db.close()

    def _execute_sql_file(
        self,
        *args,
        filename: str,
        sql_params: typing.List[typing.Union[str, int]] = [],
        **kwargs
    ) -> None:
        """ Execute the SQL from an external file """
        sql_file_path = os.path.join(
            settings.BASE_DIR, self.ETL_STEPS_DIR, filename
        )
        with open(sql_file_path, "r") as sql_file:
            sql = sql_file.read()
            self.postgres_cursor.execute(sql, sql_params)

    def _save_all_model_objects(self, *args, app_name: str, model_name: str, **kwargs) -> None:
        """ Call save() on all objects in model, mostly to update image dimension fields """

        model = django_apps.get_model(app_name, model_name)
        for object in model.objects.all():
            object.save()

    def repair_media(self, *args, app_name: str, model_name: str, field_name: str, **kwargs) -> None:
        """ Repair media and update path on specified FileField """

        model = django_apps.get_model(app_name, model_name)
        field = model._meta.get_field(field_name)
        assert (isinstance(field, django_models.FileField))
        db_table_name = model._meta.db_table
        db_column_name = field.column

        select_media_query = f"SELECT id,{db_column_name} FROM {db_table_name};"
        self.postgres_cursor.execute(select_media_query)
        results = db_utils.namedtuplefetchall(self.postgres_cursor)
        for result in results:
            old_path = getattr(result, db_column_name, "")
            new_base_path = getattr(field, "upload_to")
            if old_path:
                new_path = etl_utils.download_to_default_storage(
                    old_path=old_path,
                    new_base_path=new_base_path,
                )
                update_media_query = f"UPDATE {db_table_name} SET {db_column_name} = %s WHERE id = %s;"
                self.postgres_cursor.execute(update_media_query, [new_path, result.id])

    def handle(self, *args, **options) -> None:
        django_management.call_command("reset_db", "--noinput", "--skip-checks", "-v0")
        django_management.call_command("migrate", "--noinput", "--skip-checks", "-v0")

        self.postgres_cursor = django_db_connection.cursor()
        sqlite_path = self._get_sqlite_file_path()

        etl_steps = [
            {
                "method": self._execute_sqlite_file,
                "kwargs": {
                    "filename": "00_clean_sqlite_db.sql"
                }
            },
            {
                "method": self._execute_sql_file,
                "kwargs": {
                    "filename": "01_fdw_create.sql",
                    "sql_params": [sqlite_path],
                },
            },
            {
                "method": self._execute_sql_file,
                "kwargs": {"filename": "02_shows_create.sql"},
            },
            {
                "method": self.repair_media,
                "kwargs": {
                    "app_name": "shows",
                    "model_name": "Show",
                    "field_name": "logo"
                },
            },
            {
                "method": self.repair_media,
                "kwargs": {
                    "app_name": "shows",
                    "model_name": "Show",
                    "field_name": "thumbnail"
                },
            },
            {
                "method": py_steps.podcasts_create.run,
            },
            {
                "method": self._execute_sql_file,
                "kwargs": {"filename": "03_flatpage.sql"},
            },
            {
                "method": self._execute_sql_file,
                "kwargs": {"filename": "04_tags.sql"},
            },
            {
                "method": self._execute_sql_file,
                "kwargs": {"filename": "05_news.sql"},
            },
            {
                "method": self._execute_sql_file,
                "kwargs": {"filename": "06_bookclub.sql"},
            },
            {
                "method": self.repair_media,
                "kwargs": {
                    "app_name": "shows",
                    "model_name": "Content",
                    "field_name": "image"
                },
            },
            {
                "method": self._execute_sql_file,
                "kwargs": {"filename": "07_videos.sql"},
            },
            {
                "method": py_steps.video_thumbnails.run,
            },
            {
                "method": self._execute_sql_file,
                "kwargs": {"filename": "08_geeknights.sql"},
            },
            {
                "method": self._execute_sql_file,
                "kwargs": {"filename": "09_totd.sql"},
            },
            {
                "method": self._execute_sql_file,
                "kwargs": {"filename": "10_tag_content.sql"},
            },
            # {
            #     "method": self._execute_sql_file,
            #     "kwargs": {"filename": "11_dedupe_tags.sql"},
            # },
            {
                "method": self._execute_sql_file,
                "kwargs": {"filename": "12_bookclub_relations.sql"},
            },
            {
                "method": self._save_all_model_objects,
                "kwargs": {
                    "app_name": "shows",
                    "model_name": "Show",
                }
            },
            {
                "method": self._save_all_model_objects,
                "kwargs": {
                    "app_name": "shows",
                    "model_name": "Content",
                }
            },
            # {
            #     "method": self._execute_sql_file,
            #     "kwargs": {"filename": "XX_fdw_drop.sql"},
            # }
        ]

        try:
            for step in tqdm.tqdm(etl_steps):
                step["method"](*step.get("args", []), **step.get("kwargs", {}))
        finally:
            self.postgres_cursor.close()
