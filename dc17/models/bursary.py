from django.db import models

from dc17.models.attendee import Attendee


class Bursary(models.Model):
    attendee = models.OneToOneField(Attendee, related_name='bursary')

    requesting_travel_bursary = models.BooleanField()
    bursary_reason_contribution = models.TextField()
    bursary_reason_plans = models.TextField()
    bursary_reason_diversity = models.TextField()
    bursary_need = models.CharField(max_length=16)
    travel_bursary = models.IntegerField()
    travel_from = models.TextField()

    def __str__(self):
        return 'Bursary <{}>'.format(self.attendee.user.username)
