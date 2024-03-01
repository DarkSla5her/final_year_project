from django.urls import path
from . import views

urlpatterns = [
    # path('', views.index, name='index'),
    # path('recommend/', views.food_recommendation, name='food_recommendation'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    # path('signingup/', views.signingup, name='signingup'),
    path('homepage/', views.homepage, name='homepage'),
    path('recommend_food/', views.recommend_food, name='recommend_food'),
    path('recommend_drink/', views.recommend_drink, name='recommend_drink'),


    path('register/', views.register, name='register')
    ]
