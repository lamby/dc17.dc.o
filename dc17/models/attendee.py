from django.conf import settings
from django.db import models


class Attendee(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                related_name='attendee')

    # Contact information
    nametag_2 = models.CharField(max_length=50)
    nametag_3 = models.CharField(max_length=50)
    emergency_contact = models.TextField()
    announce_me = models.BooleanField()
    register_announce = models.BooleanField()
    register_discuss = models.BooleanField()

    # Conference details
    debcamp = models.BooleanField()
    open_day = models.BooleanField()
    debconf = models.BooleanField()
    fee = models.CharField(max_length=5)
    arrival = models.DateTimeField(null=True)
    departure = models.DateTimeField(null=True)
    final_dates = models.BooleanField()
    reconfirm = models.BooleanField()

    # Personal information
    t_shirt_cut = models.CharField(max_length=1)
    t_shirt_size = models.CharField(max_length=8)
    gender = models.CharField(max_length=1)
    country = models.CharField(max_length=2)
    languages = models.CharField(max_length=50)

    # Misc
    billing_address = models.TextField()
    notes = models.TextField()

    def __str__(self):
        return 'Attendee <{}>'.format(self.user.username)
