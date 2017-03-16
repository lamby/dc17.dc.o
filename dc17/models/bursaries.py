from django.db import models

class Bursaries(models.Model):

    bursary = CharField(max_length=50)
    bursary_reason_contribution = TextField()
    bursary_reason_plans = TextField()
    bursary_reason_diversity = TextField()
    bursary_need = CharField(max_length=50)
    travel_bursary = IntegerField()
    travel_from = CharField(max_length=50)


    def __str__(self):
        return self.title
