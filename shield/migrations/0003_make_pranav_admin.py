from django.db import migrations


def make_pranav_admin(apps, schema_editor):
    User = apps.get_model("auth", "User")

    try:
        user = User.objects.get(username="pranav")
        user.is_staff = True
        user.is_superuser = True
        user.save()
    except User.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ("shield", "0002_analysis_user"),
    ]

    operations = [
        migrations.RunPython(make_pranav_admin),
    ]
