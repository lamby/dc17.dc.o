from django.db import models

from django.contrib.auth.models import User


class Bursary(models.Model):
    # Linked to User rather than Attendee, so we don't lose track if someone
    # unregisters
    user = models.OneToOneField(User, related_name='bursary')

    requesting_travel_bursary = models.BooleanField()
    bursary_reason_contribution = models.TextField()
    bursary_reason_plans = models.TextField()
    bursary_reason_diversity = models.TextField()
    bursary_need = models.CharField(max_length=16)
    travel_bursary = models.IntegerField()
    travel_from = models.TextField()

    def __str__(self):
        return 'Bursary <{}>'.format(self.attendee.user.username)
