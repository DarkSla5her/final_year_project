from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User




class SignUpForm(UserCreationForm):
    class Meta:
        model = User # Use your custom user model
        fields = ["email", "first_name", "last_name", "password1", "password2"]


# class LoginForm(AuthenticationForm):
#     email = forms.EmailField(label="Email", max_length=255)
#     password = forms.CharField(label="Password", widget=forms.PasswordInput)

#     def clean(self):
#         email = self.cleaned_data.get("email")
#         password = self.cleaned_data.get("password")

#         if email and password:
#             user = User.objects.filter(email=email).first()
#             if not user:
#                 raise forms.ValidationError("Invalid email or password")
#             if not user.check_password(password):
#                 raise forms.ValidationError("Invalid email or password")
#             if not user.is_active:
#                 raise forms.ValidationError("User is inactive")

#         return self.cleaned_data

# # forms.py


# class SignUpForm(UserCreationForm):
#     class Meta:
#         model = User # Use your custom user model
#         fields = ["email", "first_name", "last_name", "password1", "password2"]

#     def clean_email(self):
#         email = self.cleaned_data.get("email")
#         if User.objects.filter(email=email).exists():
#             raise forms.ValidationError("Email already in use")
#         return email

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.username = user.email
#         if commit:
#             user.save()
#         return user
