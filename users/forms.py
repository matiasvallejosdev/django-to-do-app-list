from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Username',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'username',
            }
        ),
    )

    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'password'
            }
        ),
    )


# How to add first name and last name to registration form
# https://stackoverflow.com/questions/66936963/how-can-i-add-first-name-and-last-name-in-my-registration-form
class SignUpForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ("username", "first_name", "last_name",
                  "email", "password1", "password2",)
