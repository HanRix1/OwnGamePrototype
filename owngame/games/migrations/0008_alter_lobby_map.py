# Generated by Django 4.2.1 on 2024-11-03 03:37

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0007_remove_question_is_answered_lobby_map'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lobby',
            name='map',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), default=[], size=None),
        ),
    ]