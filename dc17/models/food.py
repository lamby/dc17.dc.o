from django.db import models


class FoodSelection(models.Model):
    description = models.CharField(max_length=300)


class Food(models.Model):
    food_selection = models.ManyToManyField(FoodSelection)
    diet = models.CharField(max_length=50)
    special_diet = models.CharField(max_length=50)

    def __str__(self):
        return self.title
