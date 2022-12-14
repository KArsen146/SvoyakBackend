# Generated by Django 4.0.1 on 2022-10-31 09:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('packs', '0004_pack_is_deprecated_pack_version_alter_pack_author_and_more'),
        ('rooms', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='room',
            name='admin',
        ),
        migrations.RemoveField(
            model_name='room',
            name='has_access',
        ),
        migrations.RemoveField(
            model_name='room',
            name='members',
        ),
        migrations.AddField(
            model_name='room',
            name='current_round',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='packs.roundingame'),
        ),
        migrations.AddField(
            model_name='room',
            name='pack',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='rooms_with_pack', to='packs.pack'),
            preserve_default=False,
        ),
    ]
