# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dc17', '0003_populate_sponsorship_packages'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bursary',
            name='travel_bursary',
            field=models.IntegerField(null=True),
        ),
    ]
