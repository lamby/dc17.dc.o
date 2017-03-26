from django.db import models

from dc17.models.attendee import Attendee


class AccommNight(models.Model):
    date = models.DateField(unique=True)

    @property
    def form_name(self):
        return str(self)

    def __str__(self):
        return self.date.isoformat()


class Accomm(models.Model):
    attendee = models.OneToOneField(Attendee, related_name='accomm')

    nights = models.ManyToManyField(AccommNight)
    requirements = models.TextField()
    alt_accomm_choice = models.CharField(max_length=16, null=True)
    childcare = models.BooleanField()
    childcare_needs = models.TextField()
    childcare_details = models.TextField()
    special_needs = models.TextField()
    family_usernames = models.TextField()

    def __str__(self):
        return 'Accomm <{}>'.format(self.attendee.user.username)
