# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Accomm',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('requirements', models.TextField()),
                ('alt_accomm_choice', models.CharField(null=True, max_length=16)),
                ('childcare', models.BooleanField()),
                ('childcare_needs', models.TextField()),
                ('childcare_details', models.TextField()),
                ('special_needs', models.TextField()),
                ('family_usernames', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='AccommNight',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('date', models.DateField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Attendee',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('nametag_2', models.CharField(max_length=50)),
                ('nametag_3', models.CharField(max_length=50)),
                ('emergency_contact', models.TextField()),
                ('announce_me', models.BooleanField()),
                ('register_announce', models.BooleanField()),
                ('register_discuss', models.BooleanField()),
                ('debcamp', models.BooleanField()),
                ('open_day', models.BooleanField()),
                ('debconf', models.BooleanField()),
                ('fee', models.CharField(max_length=5)),
                ('arrival', models.DateTimeField(null=True)),
                ('departure', models.DateTimeField(null=True)),
                ('final_dates', models.BooleanField()),
                ('reconfirm', models.BooleanField()),
                ('t_shirt_cut', models.CharField(max_length=1)),
                ('t_shirt_size', models.CharField(max_length=8)),
                ('gender', models.CharField(max_length=1)),
                ('country', models.CharField(max_length=2)),
                ('languages', models.CharField(max_length=50)),
                ('billing_address', models.TextField()),
                ('notes', models.TextField()),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL, related_name='attendee')),
            ],
        ),
        migrations.CreateModel(
            name='Bursary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('request', models.CharField(max_length=32, null=True)),
                ('reason_contribution', models.TextField()),
                ('reason_plans', models.TextField()),
                ('reason_diversity', models.TextField()),
                ('need', models.CharField(max_length=16)),
                ('travel_bursary', models.IntegerField()),
                ('travel_from', models.TextField()),
                ('team_notes', models.TextField()),
                ('rank', models.IntegerField(null=True)),
                ('approved_accomm', models.NullBooleanField()),
                ('approved_travel', models.IntegerField(null=True)),
                ('reimbursed_amount', models.IntegerField(default=0)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL, related_name='bursary')),
            ],
        ),
        migrations.CreateModel(
            name='Food',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('diet', models.CharField(max_length=16)),
                ('special_diet', models.TextField()),
                ('attendee', models.OneToOneField(to='dc17.Attendee', related_name='food')),
            ],
        ),
        migrations.CreateModel(
            name='Meal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('date', models.DateField(db_index=True)),
                ('meal', models.CharField(max_length=16)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='meal',
            unique_together=set([('date', 'meal')]),
        ),
        migrations.AddField(
            model_name='food',
            name='meals',
            field=models.ManyToManyField(to='dc17.Meal'),
        ),
        migrations.AddField(
            model_name='accomm',
            name='nights',
            field=models.ManyToManyField(to='dc17.AccommNight'),
        ),
        migrations.AddField(
            model_name='accomm',
            name='attendee',
            field=models.OneToOneField(to='dc17.Attendee', related_name='accomm'),
        ),
    ]
