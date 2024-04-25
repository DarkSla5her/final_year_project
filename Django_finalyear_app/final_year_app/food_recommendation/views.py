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
        else:#which uses a random in-built function to generate a recommendation
            recommended_drink = "No drinks available for the selected type."#if nothing is available this is returned

        return render(request, 'food_recommendation/recommend_drink.html', {'recommended_drink': recommended_drink})# whatever is in recommend_drink is shown to user

    return render(request, 'food_recommendation/recommend_drink.html')#if method is not POST default render is returned

def recommend_food(request):#function that takes request as an argument
    if request.method == 'POST':#form in the frontend has been submitted
        course = request.POST.get('course').strip()
        cuisine = request.POST.get('cuisine').strip()#gets the values from the form fields and removes
        allergies_str = request.POST.get('allergies').strip()#any leading or trailing white spaces
        vegetarian = request.POST.get('vegetarian', None)
        meat = request.POST.get('meat', None)

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
        if meat:#checks if the meat is specified in the meat column which can contain multiple meat types seperated by commas
            ans = ans[ans['Meat'].apply(lambda x: meat.lower() in str(x).lower().split(','))]

        # Filter out any foods that contain the users specified allergies
        for allergy in allergies:
            ans = ans[~ans['Allergies'].str.contains(allergy, case=False, na=False)]

        if ans.empty:
            print("No data found after filtering.")#checks if there are no recommendations left after filtering
            recommendations = "No recommendations found."
        else:#if there are recommendations calls this function to get a recommendation and randomly selects one
            recommendations = food_recommendation_helper(ans,ans['Food'].tolist(), food_data, allergies, cuisine, vegetarian, meat)
            if recommendations:
                recommendations = random.choice(recommendations)#random used to generate a random recommendation
            else:
                recommendations = "No recommendations found."
        #renders the template and passes the recommendations and selected course values to be displayed 
        return render(request, 'food_recommendation/recommend_food.html', {'recommendations': recommendations, 'selected_course': course})
    else:
        return render(request, 'food_recommendation/recommend_food.html')#if method not POST


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
