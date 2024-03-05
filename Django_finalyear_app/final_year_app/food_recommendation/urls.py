from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('homepage/', views.homepage, name='homepage'),
    path('recommend_food/', views.recommend_food, name='recommend_food'),
    path('recommend_drink/', views.recommend_drink, name='recommend_drink'),
    path('account/', views.account, name='account'),

    ]