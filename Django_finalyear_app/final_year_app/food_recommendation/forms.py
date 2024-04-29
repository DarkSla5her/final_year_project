from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


#required form fields
class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

#metadata about the form 
    class Meta:
        model = User#indicates form is associated with the built in user model
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")#specifies fields that should be included in the form

    def save(self, commit=True):
        #calls the save() method of the parent class (UserCreationForm) with commit=False to create the user instance without saving it to the database yet.
        user = super(SignUpForm, self).save(commit=False)

        #assigns cleaned details to the corresponding fields of the user object
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user


