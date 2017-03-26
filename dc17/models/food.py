from django.db import models

from dc17.models.attendee import Attendee


class Meal(models.Model):
    date = models.DateField(db_index=True)
    meal = models.CharField(max_length=16)

    def __str__(self):
        return '{}: {}'.format(self.date.isoformat(), self.meal)

    class Meta:
        unique_together = ('date', 'meal')


class Food(models.Model):
    attendee = models.OneToOneField(Attendee, related_name='food')

    meals = models.ManyToManyField(Meal)
    diet = models.CharField(max_length=16)
    special_diet = models.TextField()

    def __str__(self):
        return 'Attendee <{}>'.format(self.attendee.user.username)
