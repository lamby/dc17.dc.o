from django.conf import settings
from django.db import models


class Bursary(models.Model):
    # Linked to User rather than Attendee, so we don't lose track if someone
    # unregisters
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                related_name='bursary')

    # Request:
    request = models.CharField(max_length=32, null=True)
    reason_contribution = models.TextField()
    reason_plans = models.TextField()
    reason_diversity = models.TextField()
    need = models.CharField(max_length=16)
    travel_bursary = models.IntegerField()
    travel_from = models.TextField()

    # Review:
    team_notes = models.TextField()
    rank = models.IntegerField(null=True)
    approved_accomm = models.NullBooleanField()
    approved_travel = models.IntegerField(null=True)
    reimbursed_amount = models.IntegerField(default=0)

    def __str__(self):
        return 'Bursary <{}>'.format(self.attendee.user.username)
