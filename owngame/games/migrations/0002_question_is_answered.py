# Generated by Django 4.2.1 on 2024-09-10 07:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='is_answered',
            field=models.BooleanField(default=False),
        ),
    ]