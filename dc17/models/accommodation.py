from django.db import models


class AccommNight(models.Model):
    description = models.CharField(max_length=300)


class Accomm(models.Model):
    accomm = models.CharField(max_length=50)
    accomm_nights = models.ManyToManyField(AccommNight)
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
