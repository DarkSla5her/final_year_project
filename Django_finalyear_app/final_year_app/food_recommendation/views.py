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
from django.http import HttpResponseBadRequest
from .models import RecommendedDrink
from .models import RecommendedFood
from django.contrib.auth.decorators import login_required

from django.contrib.auth.views import redirect_to_login

# the above are the required imports to run the application

def signup(request):
    print("Signup view accessed")  # Confirm the view is being accessed
    if request.method == 'POST':
        print("Processing POST request")  # Confirm form submission
        form = SignUpForm(request.POST)
        # if the form details are good the user can sign up
        if form.is_valid():
            print("Form is valid")
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully')
            # once signed up redirect to login page
            return redirect('login')
        else:
            print("Form is not valid")
            # Pass form errors to template context
            context = {'form': form}
            return render(request, 'food_recommendation/signup.html', context)
    else:
        form = SignUpForm()
    return render(request, 'food_recommendation/signup.html', {'form': form})

def login_view(request):
    # form has been submitted
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        # if form details are valid user is authenticated 
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)  # if login is successful a new session starts for the user
                # Check if the user was redirected from a restricted page, if not they are redirected to the homepage
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                else:
                    return redirect('homepage') 
            else:
                messages.error(request, "Invalid username or password.")#if authentication fails
        else:
            messages.error(request, "Invalid form data.")#if submitted data is not valid 
    else:
        # Check if the user was redirected from a restricted page but did not submit a login form
        next_url = request.GET.get('next')
        if next_url:
            messages.error(request, "You must be logged in to access this page.")
        form = AuthenticationForm()#prepares any empty form to be displayed 
    return render(request, 'food_recommendation/login.html', {'form': form})#sent as HTTP response 

# if the user selects the logout button, the session ends and the user is logged out. the user cannot access the pages without logging in again
def logout_view(request):
    if request.method == "POST":
        logout(request)  # End the user's session
        messages.success(request, "You have been logged out successfully.")
    return redirect("login")

@login_required(login_url='login')
def account(request):
     return render(request, 'food_recommendation/account.html')

@login_required(login_url='login')
def homepage(request):
     return render(request, 'food_recommendation/homepage.html')
 
@login_required(login_url='login')
def recommend_drink(request):#the drinks function to recommend a drink, takes request as an argument
    if request.method == 'POST':#checks if the request is post which means that it is submitted
        alcoholic_or_non_alcoholic = request.POST.get('alcoholic_or_non_alcoholic')
        drink_type = request.POST.get('drink_type')#retrieves the values from the form
        wine_subtype = request.POST.get('wine_subtype')

        # Reads the drinks data from the CSV file
        drinks = pd.read_csv("food_recommendation/drinks.csv")  

        # Filter drinks based on user preferences
        if alcoholic_or_non_alcoholic == 'Alcoholic':#checks if user has selected alcoholic
            if drink_type == 'Wine':#checks if user has selected wine, if they have they will be asked to select a subtype
                drinks = drinks[drinks['Type'] == wine_subtype]
            else:
                drinks = drinks[drinks['Type'] == drink_type]#otherwise filters normally for other alcoholic drinks
        else:
            if drink_type == 'Soft':#checks if soft has been selected to select only the drinks that contain the word 'soft'
                drinks = drinks[drinks['Type'].str.contains('Soft', case=False)]
            else:
                drinks = drinks[drinks['Type'] == drink_type]

        # Filtered drinks
        filtered_drinks = drinks[['Name', 'Type']]#new data frame created containing name and type 
        drink_names = filtered_drinks['Name'].tolist()#takes the name and converts it into a list

        if drink_names:
            recommended_drink = random.choice(drink_names)#checks if there are drinks in the drink_names list, if there are it is assigned to recommend_drink
            # RecommendedDrink.objects.create(drink_name=recommended_drink)
            RecommendedDrink.objects.create(drink_name=recommended_drink, user=request.user)
        else:#which uses a random in-built function to generate a recommendation
            recommended_drink = "No drinks available for the selected type."#if nothing is available this is returned

        return render(request, 'food_recommendation/recommend_drink.html', {'recommended_drink': recommended_drink})# whatever is in recommend_drink is shown to user

    return render(request, 'food_recommendation/recommend_drink.html')#if method is not POST default render is returned

# a decorator that only allows authenticated users to access this view
@login_required(login_url='login')
def view_recommendations(request):
    # shows the past drink recommendations for the current user that is logged in. based on user
    past_recommendations = RecommendedDrink.objects.filter(user=request.user).order_by('-recommended_on')
    print(past_recommendations) 
    return render(request, 'food_recommendation/view_recommendations.html', {'past_recommendations': past_recommendations})

# used to identify the function as login required to run or be accessed
@login_required(login_url='login')
def recommend_food(request):#request as its argument 
    if request.method == 'POST':#checks if form has been submitted
        course = request.POST.get('course')
        if course is not None:#checks if value is not none and strips whitespaces
            course = course.strip()

        cuisine = request.POST.get('cuisine')
        if cuisine is not None:#checks if value is not none and strips whitespaces
            cuisine = cuisine.strip()

        allergies_str = request.POST.get('allergies')
        if allergies_str is not None:#checks if value is not none and strips whitespaces
            allergies_str = allergies_str.strip()
        else:
            allergies_str = ''

        vegetarian = request.POST.get('vegetarian', None)
        meat = request.POST.get('meat', None)
        # if any of the required fields are left empty the form will not submit and an error message will be displayed
        if not course or not cuisine or (allergies_str == '' and 'No allergies' not in request.POST.getlist('allergies')):
            error_message = "All required fields must be filled in."#error message shown
            return render(request, 'food_recommendation/recommend_food.html', {'error_message': error_message})

        # Convert allergies string to a list splitting it by commas and removing any empty strings
        allergies = [allergy.strip() for allergy in allergies_str.split(',') if allergy.strip()]

        # Constructs the absolute path to the CSV files
        food_csv_path = os.path.join(settings.BASE_DIR, 'food_recommendation', 'food_dataset.csv')

        # Reads the dataset into a pandas data frame
        food_data = pd.read_csv(food_csv_path)

        # Strip whitespaces from specific columns in the food_data data frame
        food_data['Food'] = food_data['Food'].str.strip()
        food_data['Meat'] = food_data['Meat'].apply(lambda x: x.strip() if isinstance(x, str) else x)
        food_data['Type_of_course'] = food_data['Type_of_course'].str.strip()
        food_data['Cuisine'] = food_data['Cuisine'].str.strip()
        food_data['Is_vegetarian'] = food_data['Is_vegetarian'].str.strip()

        # Filters the food_data data frame based on user course and cuisine
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

        # Filter out any foods that contain the users specified allergies
        for allergy in allergies:
            ans = ans[~ans['Allergies'].str.contains(allergy, case=False, na=False)]

        if ans.empty:
            print("No data found after filtering.")#if empty print this as there is no data
            recommendations = "No recommendations found."
        else:
            #generates food based recommendations based on filtered data
            recommendations = food_recommendation_helper(ans, ans['Food'].tolist(), food_data, allergies, cuisine, vegetarian, meat)
            if recommendations:
                recommendations = random.choice(recommendations)#random choice everytime it is run
            else:
                recommendations = "No recommendations found."
        
        if recommendations:
            # Save the recommended food to the database. this is to be used for past recommendations. 
            RecommendedFood.objects.create(food_name=recommendations, user=request.user)#recommendations specific to the user
        return render(request, 'food_recommendation/recommend_food.html', {'recommendations': recommendations, 'selected_course': course})
    else:
        return render(request, 'food_recommendation/recommend_food.html')

# a decorator that only allows authenticated users to access pages
@login_required(login_url='login')
def view_past_food(request):
    # shows the past food recommendations for the current user that is logged in. based on user
    past_recommendations = RecommendedFood.objects.filter(user=request.user).order_by('-recommended_on')
    return render(request, 'food_recommendation/view_past_food.html', {'past_recommendations': past_recommendations})


def food_recommendation_helper(food_database,food_names, food_data, allergies, selected_cuisine, vegetarian, meat):#takes several arguments
    
    # testing and debugging code printed in terminal
    selected_food_data = food_database
    print("Testing...")
    print (selected_food_data)

    # Check if there is data left after filtering, returns empty list if it is
    if selected_food_data.empty:
        return []

    # Creates dummies for the selected food column using one-hot encoding
    food_dummies = pd.get_dummies(selected_food_data['Food'])
    selected_food_data.reset_index(drop=True, inplace=True)
    n_samples = len(food_dummies)#Calculates the number of samples and determines the number of neighbors to use in the NearestNeighbors model
    n_neighbors = min(11, n_samples)  # Adjust neighbors based on available samples, max 11 neigbors

    # If there are more than 1 sample, it initializes and fits a NearestNeighbors model using cosine similarity as the distance metric and brute-force algorithm
    if n_samples > 1:
        model = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=n_neighbors, n_jobs=-1)
        model.fit(food_dummies)
    else:
        # Not enough samples to fit the model, return available foods
        return selected_food_data['Food'].tolist()

    recommendations = []

    # Generate recommendations for each food name
    #each food name in food_names, it finds the closest matches using the NearestNeighbors model 
    #and adds them to the recommendations list if they are not in the allergies list.
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

    # Add any unmatched food items to the recommendations list 
    for food_name in food_names:
        if food_name not in recommendations:
            recommendations.append(food_name)

    return recommendations #return the final list of recommendations
