from django.db import models


class ImportRecord(models.Model):
    import_time = models.DateTimeField(auto_now_add=True)
    old_id = models.BigIntegerField()
    old_table_name = models.TextField()
    new_id = models.BigIntegerField()
    new_table_name = models.TextField()
    source_record = models.JSONField()

    def __str__(self):
        return f"Import {self.old_table_name}:{self.old_id} -> {self.new_table_name}:{self.new_id}"
