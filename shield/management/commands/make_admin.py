from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Make the pranav user a Django superuser"

    def handle(self, *args, **kwargs):
        username = "pranav"

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR("User 'pranav' was not found.")
            )
            return

        user.is_staff = True
        user.is_superuser = True
        user.save()

        self.stdout.write(
            self.style.SUCCESS(
                "pranav is now a Django superuser."
            )
        )