# Generated by Django 4.0.1 on 2022-05-04 02:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('packs', '0002_round_pack_title_theme_round_pack_question'),
    ]

    operations = [
        migrations.AddField(
            model_name='pack',
            name='author',
            field=models.TextField(blank=True, db_index=True, max_length=32, null=True),
        ),
    ]
