# Generated by Django 3.2.9 on 2021-11-19 13:41

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0017_alter_device_date_added'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='date_added',
            field=models.DateTimeField(default=datetime.datetime(2021, 11, 19, 13, 41, 42, 789919, tzinfo=utc)),
        ),
    ]
