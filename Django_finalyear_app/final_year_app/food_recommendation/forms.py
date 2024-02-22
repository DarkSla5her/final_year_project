from django import forms

class FoodRecommendationForm(forms.Form):
    vegn = forms.ChoiceField(choices=[('veg', 'Vegetables'), ('non-veg', 'Non-vegetarian')], initial='non-veg')
    cuisine = forms.ChoiceField(choices=[('Healthy Food', 'Healthy Food'), ('Snack', 'Snack'), ...])
    val = forms.IntegerField(label='Rating', min_value=0, max_value=10)
