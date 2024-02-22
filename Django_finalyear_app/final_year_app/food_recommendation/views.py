from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd 
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors

def index(request):
    #return render (request,"food_recommendation/index.html")
    return HttpResponse("Hello, world. You're at the polls index.")

def food_recommendation(request):
    if request.method == 'POST':
        # Process form data
        vegn = request.POST.get('vegn')
        cuisine = request.POST.get('cuisine')
        val = int(request.POST.get('val'))

        # Load data
        food = pd.read_csv("food.csv")
        ratings = pd.read_csv("ratings.csv")
        combined = pd.merge(ratings, food, on='Food_ID')

        # Filter data based on user preferences
        ans = combined.loc[(combined.C_Type == cuisine) & (combined.Veg_Non == vegn) & (combined.Rating >= val),['Name','C_Type','Veg_Non']]
        names = ans['Name'].tolist()
        x = np.array(names)
        ans1 = np.unique(x)

        # Run recommender
        dataset = ratings.pivot_table(index='Food_ID',columns='User_ID',values='Rating')
        dataset.fillna(0,inplace=True)
        csr_dataset = csr_matrix(dataset.values)
        dataset.reset_index(inplace=True)

        model = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=20, n_jobs=-1)
        model.fit(csr_dataset)

        recommendations = food_recommendation_helper(ans1, food, dataset, model)

        return render(request, 'food_recommendation/recommendations.html', {'recommendations': recommendations})
    return render(request, 'templates/food_recommendation/index.html')

def food_recommendation_helper(food_names, food_data, dataset, model):
    recommendations = []
    for food_name in food_names:
        n = 10
        FoodList = food_data[food_data['Name'].str.contains(food_name)]  
        if len(FoodList):        
            Foodi= FoodList.iloc[0]['Food_ID']
            Foodi = dataset[dataset['Food_ID'] == Foodi].index[0]
            distances , indices = model.kneighbors(csr_dataset[Foodi], n_neighbors=n+1)    
            Food_indices = sorted(list(zip(indices.squeeze().tolist(),distances.squeeze().tolist())), key=lambda x: x[1])[:0:-1]
            for val in Food_indices:
                Foodi = dataset.iloc[val[0]]['Food_ID']
                i = food_data[food_data['Food_ID'] == Foodi].index
                recommendations.append(food_data.iloc[i]['Name'].values[0])
    return recommendations
