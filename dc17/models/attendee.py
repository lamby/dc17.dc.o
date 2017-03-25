from django.db import models


class Attendee(models.Model):
    # Contact information
    name = models.CharField()  # FIXME
    nametag_2 = models.CharField(max_length=50)
    nametag_3 = models.ForeignKey(User, related_name='username')
    email = models.ForeignKey(User)
    phone = models.ForeignKey(UserProfile, related_name='contact_number')
    emergency_contact = models.CharField()
    announce_me = models.BooleanField()
    register_announce = models.BooleanField()
    register_discuss = models.BooleanField()

    # Conference details
    debcamp = models.BooleanField()
    open_day = models.BooleanField()
    debconf = models.BooleanField()
    fee = models.CharField(max_length=50)
    arrival = models.DateTimeField()
    departure = models.DateTimeField()
    final_dates = models.CharField(max_length=50)
    reconfirm = models.BooleanField()

    # Personal information
    t_shirt_cut = models.CharField(max_length=50)
    t_shirt_size = models.CharField(max_length=50)
    gender = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    languages = models.CharField(max_length=50)

    def __str__(self):
        return self.title
