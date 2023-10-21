from django.core import management as django_management
from django.contrib import auth
from media import models as media_models


class Command(django_management.base.BaseCommand):
    help = "Run the ETL then create other things for local dev"

    def handle(self, *args, **options) -> None:
        # Reset database and perform etl
        django_management.call_command("etl")

        # Create superuser
        django_management.call_command(
            "createsuperuser",
            "--noinput",
            username="admin",
            email="admin@frontrowcrew.com",
        )
        User = auth.get_user_model()
        user = User.objects.all()[0]
        user.set_password("admin")
        user.save()

        # Create FTPDestination
        media_models.FTPDestination.objects.create(
            name="AlpineFTP",
            host="ftp",
            username="alpineftp",
            password="alpineftp",
        )
