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
from .forms import SignUpForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
import random

def signup(request):
    print("Signup view accessed")  # Confirm the view is being hit
    if request.method == 'POST':
        print("Processing POST request")  # Confirm form submission
        form = SignUpForm(request.POST)
        if form.is_valid():
            print("Form is valid")
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully')
            return redirect('login')
        else:
            print("Form is not valid")
            # Pass form errors to template context
            context = {'form': form}
            return render(request, 'food_recommendation/signup.html', context)
    else:
        form = SignUpForm()
    return render(request, 'food_recommendation/signup.html', {'form': form})


@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('homepage')  # Redirect to the homepage
        # Display error message for invalid username or password
        messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'food_recommendation/login.html', {'form': form})


def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("home")

def account(request):
     return render(request, 'food_recommendation/account.html')
 
def homepage(request):
     return render(request, 'food_recommendation/homepage.html')
 
def recommend_drink(request):
    if request.method == 'POST':
        alcoholic_or_non_alcoholic = request.POST.get('alcoholic_or_non_alcoholic')
        drink_type = request.POST.get('drink_type')
        wine_subtype = request.POST.get('wine_subtype')

        # Read drinks data from CSV file
        drinks = pd.read_csv("food_recommendation/drinks.csv")  # Update with the actual path

        # Filter drinks based on user preferences
        if alcoholic_or_non_alcoholic == 'Alcoholic':
            if drink_type == 'Wine':
                drinks = drinks[drinks['Type'] == wine_subtype]
            else:
                drinks = drinks[drinks['Type'] == drink_type]
        else:
            if drink_type == 'Soft':
                drinks = drinks[drinks['Type'].str.contains('Soft', case=False)]
            else:
                drinks = drinks[drinks['Type'] == drink_type]

        # Filtered drinks
        filtered_drinks = drinks[['Name', 'Type']]
        drink_names = filtered_drinks['Name'].tolist()

        if drink_names:
            recommended_drink = random.choice(drink_names)
        else:
            recommended_drink = "No drinks available for the selected type."

        return render(request, 'food_recommendation/recommend_drink.html', {'recommended_drink': recommended_drink})

    return render(request, 'food_recommendation/recommend_drink.html')

def recommend_food(request):
    if request.method == 'POST':
        course = request.POST.get('course').strip()
        cuisine = request.POST.get('cuisine').strip()
        allergies_str = request.POST.get('allergies').strip()
        vegetarian = request.POST.get('vegetarian', None)
        meat = request.POST.get('meat', None)

        # Convert allergies string to a list
        allergies = [allergy.strip() for allergy in allergies_str.split(',') if allergy.strip()]

        # Construct absolute paths for the CSV files
        food_csv_path = os.path.join(settings.BASE_DIR, 'food_recommendation', 'food_dataset.csv')

        # Load data using absolute paths
        food_data = pd.read_csv(food_csv_path)

        # Strip whitespaces from the 'Food' and 'Meat' columns
        food_data['Food'] = food_data['Food'].str.strip()
        food_data['Meat'] = food_data['Meat'].apply(lambda x: x.strip() if isinstance(x, str) else x)
        food_data['Type_of_course'] = food_data['Type_of_course'].str.strip()
        food_data['Cuisine'] = food_data['Cuisine'].str.strip()
        food_data['Is_vegetarian'] = food_data['Is_vegetarian'].str.strip()

        # Filter data based on user preferences and allergies
        ans = food_data[
                    (food_data['Type_of_course'] == course) &
                    (food_data['Cuisine'] == cuisine)
                ]
        
        # Filter by vegetarian if specified
        if vegetarian:
            ans = ans[ans['Is_vegetarian'] == vegetarian]

        # Filter by meat if specified
        if meat:
            ans = ans[ans['Meat'].apply(lambda x: meat.lower() in str(x).lower().split(','))]

        # Filter out any allergies
        for allergy in allergies:
            ans = ans[~ans['Allergies'].str.contains(allergy, case=False, na=False)]

        if ans.empty:
            print("No data found after filtering.")
            recommendations = "No recommendations found."
        else:
            recommendations = food_recommendation_helper(ans,ans['Food'].tolist(), food_data, allergies, cuisine, vegetarian, meat)
            if recommendations:
                recommendations = random.choice(recommendations)
            else:
                recommendations = "No recommendations found."

        return render(request, 'food_recommendation/recommend_food.html', {'recommendations': recommendations, 'selected_course': course})
    else:
        return render(request, 'food_recommendation/recommend_food.html')


def food_recommendation_helper(food_database,food_names, food_data, allergies, selected_cuisine, vegetarian, meat):
    
    # testing and debugging code
    selected_food_data = food_database
    print("Testing...")
    print (selected_food_data)

    # Check if there is data left after filtering
    if selected_food_data.empty:
        return []

    # Create dummies for selected food data
    food_dummies = pd.get_dummies(selected_food_data['Food'])
    selected_food_data.reset_index(drop=True, inplace=True)
    n_samples = len(food_dummies)
    n_neighbors = min(11, n_samples)  # Adjust neighbors based on available samples

    # Fit NearestNeighbors model
    if n_samples > 1:
        model = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=n_neighbors, n_jobs=-1)
        model.fit(food_dummies)
    else:
        # Not enough samples to fit the model, return available foods
        return selected_food_data['Food'].tolist()

    recommendations = []

    # Generate recommendations for each food name
    for food_name in food_names:
        FoodList = selected_food_data[selected_food_data['Food'].str.contains(food_name)]
        if not FoodList.empty:
            Foodi = FoodList.iloc[0]['Food']
            Foodi_index = selected_food_data[selected_food_data['Food'] == Foodi].index.to_list()

            if Foodi_index:
                Foodi_index = Foodi_index[0]
                distances, indices = model.kneighbors(food_dummies.iloc[Foodi_index].values.reshape(1, -1), n_neighbors=n_neighbors)
                Food_indices = indices.squeeze()[1:]

                for idx in Food_indices:
                    if idx < len(selected_food_data):
                        matching_food = selected_food_data.loc[idx]
                        if matching_food['Food'] not in allergies and matching_food['Food'] not in recommendations:
                            recommendations.append(matching_food['Food'])

    # Add any unmatched food items to recommendations
    for food_name in food_names:
        if food_name not in recommendations:
            recommendations.append(food_name)

    return recommendations
