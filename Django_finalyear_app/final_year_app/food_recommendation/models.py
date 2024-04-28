from django.db import models
from django.contrib.auth.models import AbstractBaseUser



class RecommendedDrink(models.Model):
    drink_name = models.CharField(max_length=100)
    recommended_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.drink_name
    
class RecommendedFood(models.Model):
    food_name = models.CharField(max_length=100)
    recommended_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.food_name