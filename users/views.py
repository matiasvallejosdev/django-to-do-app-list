from django.shortcuts import render, redirect

from django.contrib.auth.views import LoginView, LogoutView

from django.contrib.auth import login
from django.views.generic.edit import FormView
# from django.contrib.auth.forms import UserCreationForm

from django.urls import reverse_lazy
from users.forms import LoginForm, SignUpForm


class LoginView(LoginView):
    template_name = 'login.html'
    fields = '__all__'
    redirect_authenticated_user = True
    authentication_form = LoginForm

    def get_success_url(self):
        return reverse_lazy('tasks:home')

    def get_context_data(self, *args, **kwargs):
        context = super(LoginView, self).get_context_data(**kwargs)
        return context


class LogoutView(LogoutView):
    next_page = reverse_lazy('home')


class RegisterView(FormView):
    template_name = 'register.html'
    form_class = SignUpForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('tasks:home')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterView, self).form_valid(form)

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('tasks:home')
        return super(RegisterView, self).get(request, *args, **kwargs)
