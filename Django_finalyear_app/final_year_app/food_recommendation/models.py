from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model 

def get_default_user():
    try:
        return get_user_model().objects.first().pk
    except get_user_model().DoesNotExist:
        return None


class RecommendedDrink(models.Model):
    drink_name = models.CharField(max_length=100)
    recommended_on = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='recommended_drinks', default=get_default_user)

    
class RecommendedFood(models.Model):
    food_name = models.CharField(max_length=100)
    recommended_on = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='recommended_foods', default=get_default_user)
