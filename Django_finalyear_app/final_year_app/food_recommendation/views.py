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
            print(form.errors.as_data())  # More detailed form errors
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
            else:
                messages.error(request, "Invalid username or password.")
        else:
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
#
# OLD WORKING CODE

# def recommend_food(request):
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
#         recommendations = random.choice(recommendations)

#         return render(request, 'food_recommendation/recommend_food.html', {'recommendations': recommendations})
#     else:
#         return render(request, 'food_recommendation/recommend_food.html')


# def food_recommendation_helper(food_names, food_data, dataset, model, csr_dataset):
#     recommendations = []
#     for food_name in food_names:
#         n = 10  # Number of neighbors
#         FoodList = food_data[food_data['Name'].str.contains(food_name)]
#         if len(FoodList):
#             Foodi = FoodList.iloc[0]['Food_ID']
#             Foodi_index = dataset[dataset['Food_ID'] == Foodi].index[0]
#             distances, indices = model.kneighbors(csr_dataset[Foodi_index], n_neighbors=n+1)
#             Food_indices = sorted(list(zip(indices.squeeze().tolist(), distances.squeeze().tolist())), key=lambda x: x[1])[:0:-1]
#             for val in Food_indices:
#                 i = dataset.iloc[val[0]]['Food_ID']
#                 matching_food = food_data[food_data['Food_ID'] == i]
#                 if not matching_food.empty:
#                     recommendations.append(matching_food.iloc[0]['Name'])
#     return recommendations

# NEW TESTING CODE


def recommend_food(request):
    if request.method == 'POST':
        course = request.POST.get('course')
        cuisine = request.POST.get('cuisine')
        allergies = request.POST.getlist('allergies')
        vegetarian = request.POST.get('vegetarian')
        meat = request.POST.get('meat')

        # Construct absolute paths for the CSV files
        food_csv_path = os.path.join(settings.BASE_DIR, 'food_recommendation', 'food_dataset.csv')

        # Load data using absolute paths
        food_data = pd.read_csv(food_csv_path)

        # Strip whitespaces from the 'Food' column
        food_data['Food'] = food_data['Food'].str.strip()

        # Filter data based on user preferences and allergies
        ans = food_data.loc[
            (food_data['Type_of_course'].str.strip() == course.strip()) & 
            (food_data['Cuisine'].str.strip() == cuisine.strip()) & 
            (~food_data['Allergies'].isin(allergies))
        ]

        # Debug: Print the contents and shape of the ans DataFrame
        print("Filtered DataFrame (ans):")
        print(ans)
        print("Shape of ans DataFrame:", ans.shape)

        if ans.empty:
            print("No data found after filtering.")
            recommendations = "No recommendations found."
        else:
            recommendations = food_recommendation_helper(ans['Food'].tolist(), food_data, allergies,cuisine, vegetarian, meat)
            if recommendations:
                recommendations = random.choice(recommendations)
            else:
                recommendations = "No recommendations found."

        return render(request, 'food_recommendation/recommend_food.html', {'recommendations': recommendations})
    else:
        return render(request, 'food_recommendation/recommend_food.html')


def food_recommendation_helper(food_names, food_data, allergies, selected_cuisine, vegetarian, meat):
    # Filter food data by selected cuisine, vegetarian, and meat
    selected_food_data = food_data[
        (food_data['Cuisine'] == selected_cuisine) &
        (food_data['Is_vegetarian'] == vegetarian) &
        (food_data['Meat'] == meat if meat else True)
    ]
    
    # If the selected_food_data is empty, return an empty list
    if selected_food_data.empty:
        return []

    # Create dummies for selected food data
    food_dummies = pd.get_dummies(selected_food_data['Food'])

    # Fit NearestNeighbors model
    model = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=20, n_jobs=-1)
    model.fit(food_dummies)

    recommendations = []

    for food_name in food_names:
        FoodList = selected_food_data[selected_food_data['Food'].str.contains(food_name)]
    
    if not FoodList.empty:
        Foodi = FoodList.iloc[0]['Food']
        
        # Check if Foodi exists in selected_food_data
        if Foodi in selected_food_data['Food'].values:
            Foodi_index = selected_food_data[selected_food_data['Food'] == Foodi].index[0]
            
            distances, indices = model.kneighbors(food_dummies.iloc[Foodi_index].values.reshape(1, -1), n_neighbors=11)
            
            # Exclude the first item as it's the food itself
            Food_indices = indices.squeeze()[1:]
            
            for idx in Food_indices:
                matching_food = selected_food_data.loc[selected_food_data.index == idx]
                
                if not matching_food.empty and matching_food['Food'].iloc[0] not in allergies:
                    recommendations.append(matching_food.iloc[0]['Food'])

    # Add any food items that are not already in recommendations
    for food_name in food_names:
        if food_name not in recommendations:
            recommendations.append(food_name)

    return recommendations
