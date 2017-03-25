# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

from dc17.dates import meals, nights


def initial_meals(apps, schema_editor):
    Meal = apps.get_model('dc17', 'Meal')
    for meal, date in meals(orga=True):
        Meal.objects.get_or_create(meal=meal, date=date)


def initial_nights(apps, schema_editor):
    AccommNight = apps.get_model('dc17', 'AccommNight')
    for night in nights(orga=True):
        AccommNight.objects.get_or_create(date=night)


class Migration(migrations.Migration):
    dependencies = [
        ('dc17', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(initial_meals),
        migrations.RunPython(initial_nights),
    ]
