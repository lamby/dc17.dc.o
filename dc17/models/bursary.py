from django.db import models


class Bursary(models.Model):
    bursary = models.CharField(max_length=50)
    bursary_reason_contribution = models.TextField()
    bursary_reason_plans = models.TextField()
    bursary_reason_diversity = models.TextField()
    bursary_need = models.CharField(max_length=50)
    travel_bursary = models.IntegerField()
    travel_from = models.CharField(max_length=50)

    def __str__(self):
        return self.title
