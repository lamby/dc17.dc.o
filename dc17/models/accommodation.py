from django.db import models

class AccommNights(models.Model):

    description = CharField(max_length=300)


class Bursaries(models.Model):

    accomm = CharField(max_length=50)
    accomm_nights = ManyToManyField(AccommNights)
    accomm_special_requirements = CharField(max_length=150)
    alt_accomm = BooleanField()
    alt_accomm_choice = CharField(max_length=50)
    special_needs = TextField()
    childcare = BooleanField()
    childcare_needs = TextField()
    childcare_details = TextField()
    family_usernames = CharField(max_length=150)


    def __str__(self):
        return self.title
