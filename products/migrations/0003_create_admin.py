import os

from django.db import migrations
from django.contrib.auth.hashers import make_password


def create_admin_user(apps, schema_editor):
    User = apps.get_model("auth", "User")

    username = os.environ.get("DJANGO_ADMIN_USERNAME")
    email = os.environ.get("DJANGO_ADMIN_EMAIL")
    password = os.environ.get("DJANGO_ADMIN_PASSWORD")

    if not username or not password:
        return

    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            "email": email or "",
            "password": make_password(password),
            "is_staff": True,
            "is_superuser": True,
            "is_active": True,
        },
    )

    if not created:
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(
            update_fields=[
                "is_staff",
                "is_superuser",
                "is_active",
            ]
        )


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0002_productspecification"),
    ]

    operations = [
        migrations.RunPython(create_admin_user),
    ]