# Generated by Django 4.0.1 on 2022-02-27 19:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_alter_room_admin'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='presenter',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='presentation_room', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='room',
            name='admin',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]