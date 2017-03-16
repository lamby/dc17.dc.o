from django.db import models

class FoodSelection(models.Model):

    description = CharField(max_length=300)


class Food(models.Model):

    food_selection = ManyToManyField(FoodSelection)
    diet = CharField(max_length=50)
    special_diet = CharField(max_length=50)


    def __str__(self):
        return self.title
