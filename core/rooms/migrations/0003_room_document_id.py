# Generated by Django 4.0.1 on 2022-11-27 23:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0002_remove_room_admin_remove_room_has_access_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='document_id',
            field=models.CharField(default=None, max_length=50),
        ),
    ]
