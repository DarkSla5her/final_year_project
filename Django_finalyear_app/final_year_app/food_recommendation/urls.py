from django.urls import path, include
from . import views
from .views import login_view, logout_view

# these paths are the only paths that you can go to whilst using the applications. all other paths will cause an error

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('homepage/', views.homepage, name='homepage'),
    path('recommend_food/', views.recommend_food, name='recommend_food'),
    path('recommend_drink/', views.recommend_drink, name='recommend_drink'),
    path('account/', views.account, name='account'),
    path('view_recommendations/', views.view_recommendations, name='view_recommendations'),
    path('view_past_food/', views.view_past_food, name='view_past_food'),
    path('logout/', logout_view, name='logout'),
    ]