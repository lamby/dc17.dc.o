# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def initial_sponsorship_packages(apps, schema_editor):
    SponsorshipPackage = apps.get_model('sponsors', 'SponsorshipPackage')
    for order, name, number, price, description in (
        (1, 'Platinum', 10, 20000, 'Platinum Sponsors'),
        (2, 'Gold', 100, 10000, 'Gold sponsors'),
        (3, 'Silver', 100, 5000, 'Silver sponsors'),
        (4, 'Bronze', 100, 2000, 'Bronze sponsors'),
        (5, 'Supporter', 100, 1999, 'Supporters'),
    ):
        SponsorshipPackage.objects.get_or_create(name=name, defaults={
            'order': order,
            'name': name,
            'number_available': number,
            'currency': '$',
            'price': price,
            'short_description': description,
            'description': description,
            'symbol': '',
        })


class Migration(migrations.Migration):
    dependencies = [
        ('dc17', '0002_populate_meals_nights'),
        ('sponsors', '0005_sponsorshippackage_symbol'),
    ]
    operations = [
        migrations.RunPython(initial_sponsorship_packages),
    ]
