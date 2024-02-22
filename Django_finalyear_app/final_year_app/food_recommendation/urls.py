from django.urls import path
from . import views

urlpatterns = [
    # path('', views.index, name='index'),
    path('recommend/', views.food_recommendation, name='food_recommendation'),
    #path('index', views.index, name='index'),
    # Other URL patterns specific to this app
]
