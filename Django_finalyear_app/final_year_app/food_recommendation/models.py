from django.db import models
from django.contrib.auth.models import AbstractBaseUser




# class User(AbstractBaseUser):
#     email = models.EmailField(unique=False, null=True, blank=True)
#     first_name = models.CharField(max_length=50)
#     last_name = models.CharField(max_length=50)

#     USERNAME_FIELD = "email"
#     REQUIRED_FIELDS = ["first_name", "last_name"]

#     def __str__(self):
#         return self.email
