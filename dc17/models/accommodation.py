from django.db import models


class AccommNights(models.Model):
    description = models.CharField(max_length=300)


class Bursaries(models.Model):
    accomm = models.CharField(max_length=50)
    accomm_nights = models.ManyToManyField(AccommNights)
    accomm_special_requirements = models.CharField(max_length=150)
    alt_accomm = models.BooleanField()
    alt_accomm_choice = models.CharField(max_length=50)
    special_needs = models.TextField()
    childcare = models.BooleanField()
    childcare_needs = models.TextField()
    childcare_details = models.TextField()
    family_usernames = models.CharField(max_length=150)

    def __str__(self):
        return self.title
