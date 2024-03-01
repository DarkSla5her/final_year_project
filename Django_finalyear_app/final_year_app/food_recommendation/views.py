from django.shortcuts import render, redirect
from django.http import HttpResponse
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
import numpy as np
from django.conf import settings
import os
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.views.decorators.csrf import csrf_exempt
# from django.contrib.auth import authenticate, login as auth_login
from .forms import SignUpForm
from django.contrib.auth import login, logout, authenticate
# from .models import User # Import your custom user model
# from .forms import SignUpForm # Import your custom user form


def register(request):
    form=  SignUpForm()
    if request.method == 'POST':
        form= SignUpForm()
        if form.is_valid():
            form.save()

    context={'form':form}

    return render(request, 'food_recommendation/register.html')





# def signup(request):
#     if request.method == 'POST':
#         form = SignUpForm(request.POST)
#         if form.is_valid():
#             form.save()
#             # Redirect to success page or any other page
#             return redirect('success')
#     else:
#         form = SignUpForm()
#     return render(request, 'food_recommendation/signup.html', {'form': form})


# @csrf_exempt
# def signup(request):
#     form= SignUpForm()
#     if request.method == "POST":
#         form = SignUpForm(request.POST)
#         if form.is_valid():
#             form.save()
#     else:
#         form = SignUpForm()
#         return render(request, 'food_recommendation/signup.html', {'form': form})



    # redirect_to = request.POST.get('next', '')  # Get the value of 'next' from POST data
    # if request.method == "POST":
    #     form = SignUpForm(request.POST)
    #     if form.is_valid():
    #         user = form.save()
    #         login(request, user)
    #         if redirect_to:  # Check if a redirection URL is provided
    #             return redirect(redirect_to)  # Redirect to the provided URL
    #         else:
    #             return redirect("homepage")  # Default redirection to homepage
    # else:
    #     form = SignUpForm()
    # return render(request, 'food_recommendation/signup.html', {'form': form})


@csrf_exempt
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})

def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("home")


# def signup_view(request):
#     if request.method == 'POST':
#         form = CustomUserCreationForm(request.POST, request.FILES)
#         if form.is_valid():
#             user = form.save()
#             return redirect('login')
#     else:
#         form = CustomUserCreationForm()
#     return render(request, 'api/spa/signup.html', {'form': form})

# def login_view(request):
#     if request.method == 'POST':
#         form = AuthenticationForm(request, data=request.POST)
#         if form.is_valid():
#             username = form.cleaned_data.get('username')
#             password = form.cleaned_data.get('password')
#             user = authenticate(username=username, password=password)
#             if user is not None:
#                 auth_login(request, user)
#                 return redirect('http://127.0.0.1:8000/')  
#     else:
#         form = AuthenticationForm()
#     return render(request, 'food_recommendation/login.html', {'form': form})


def login(request):
    return render(request, 'food_recommendation/login.html')

def signup(request):
    return render(request, 'food_recommendation/signup.html')

def homepage(request):
     return render(request, 'food_recommendation/homepage.html')

def recommend_drink(request):
     return render(request, 'food_recommendation/recommend_drink.html')

def recommend_food(request):
    if request.method == 'POST':
        vegn = request.POST.get('vegn')
        cuisine = request.POST.get('cuisine')
        val = int(request.POST.get('val'))

        # Construct absolute paths for the CSV files
        food_csv_path = os.path.join(settings.BASE_DIR, 'food_recommendation', 'food.csv')
        ratings_csv_path = os.path.join(settings.BASE_DIR, 'food_recommendation', 'ratings.csv')

        # Load data using absolute paths
        food = pd.read_csv(food_csv_path)
        ratings = pd.read_csv(ratings_csv_path)
        combined = pd.merge(ratings, food, on='Food_ID')

        # Filter data based on user preferences
        ans = combined.loc[(combined['C_Type'] == cuisine) & (combined['Veg_Non'] == vegn) & (combined['Rating'] >= val), ['Name', 'C_Type', 'Veg_Non']]
        names = ans['Name'].tolist()
        ans1 = np.unique(np.array(names))

        # Run recommender
        dataset = ratings.pivot_table(index='Food_ID', columns='User_ID', values='Rating')
        dataset.fillna(0, inplace=True)
        csr_dataset = csr_matrix(dataset.values)
        dataset.reset_index(inplace=True)

        model = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=20, n_jobs=-1)
        model.fit(csr_dataset)

        recommendations = food_recommendation_helper(ans1, food, dataset, model, csr_dataset)

        return render(request, 'food_recommendation/recommendations.html', {'recommendations': recommendations})
    else:
        return render(request, 'food_recommendation/recommend_food.html')


# def food_recommendation(request):
#     if request.method == 'POST':
#         vegn = request.POST.get('vegn')
#         cuisine = request.POST.get('cuisine')
#         val = int(request.POST.get('val'))

#         # Construct absolute paths for the CSV files
#         food_csv_path = os.path.join(settings.BASE_DIR, 'food_recommendation', 'food.csv')
#         ratings_csv_path = os.path.join(settings.BASE_DIR, 'food_recommendation', 'ratings.csv')

#         # Load data using absolute paths
#         food = pd.read_csv(food_csv_path)
#         ratings = pd.read_csv(ratings_csv_path)
#         combined = pd.merge(ratings, food, on='Food_ID')

#         # Filter data based on user preferences
#         ans = combined.loc[(combined['C_Type'] == cuisine) & (combined['Veg_Non'] == vegn) & (combined['Rating'] >= val), ['Name', 'C_Type', 'Veg_Non']]
#         names = ans['Name'].tolist()
#         ans1 = np.unique(np.array(names))

#         # Run recommender
#         dataset = ratings.pivot_table(index='Food_ID', columns='User_ID', values='Rating')
#         dataset.fillna(0, inplace=True)
#         csr_dataset = csr_matrix(dataset.values)
#         dataset.reset_index(inplace=True)

#         model = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=20, n_jobs=-1)
#         model.fit(csr_dataset)

#         recommendations = food_recommendation_helper(ans1, food, dataset, model, csr_dataset)

#         return render(request, 'food_recommendation/recommendations.html', {'recommendations': recommendations})
#     else:
#         return render(request, 'food_recommendation/recommend_food.html')



def food_recommendation_helper(food_names, food_data, dataset, model, csr_dataset):
    recommendations = []
    for food_name in food_names:
        n = 10  # Number of neighbors
        FoodList = food_data[food_data['Name'].str.contains(food_name)]
        if len(FoodList):
            Foodi = FoodList.iloc[0]['Food_ID']
            Foodi_index = dataset[dataset['Food_ID'] == Foodi].index[0]
            distances, indices = model.kneighbors(csr_dataset[Foodi_index], n_neighbors=n+1)
            Food_indices = sorted(list(zip(indices.squeeze().tolist(), distances.squeeze().tolist())), key=lambda x: x[1])[:0:-1]
            for val in Food_indices:
                i = dataset.iloc[val[0]]['Food_ID']
                matching_food = food_data[food_data['Food_ID'] == i]
                if not matching_food.empty:
                    recommendations.append(matching_food.iloc[0]['Name'])
    return recommendations