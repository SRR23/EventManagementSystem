from django.views.generic import View
from .models import CustomUser
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from .forms import UserRegistrationForm, LoginForm, UserProfileUpdateForm

class RegisterView(View):
    form_class = UserRegistrationForm
    template_name = 'register.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log in the user after registration
            messages.success(request, 'Registration successful!')
            return redirect('login')  # Redirect to login page after successful registration
        return render(request, self.template_name, {'form': form})



class LoginView(View):
    form_class = LoginForm
    template_name = 'login.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        context = {
            "form": form
        }
        context['current_path'] = self.request.path
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, 'Logged in successfully!')
                return redirect('home')  # Redirect to home after login
            else:
                messages.warning(request, 'Invalid credentials')
        return render(request, self.template_name, {'form': form})


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, 'Logged out successfully!')
        return redirect('login')  # Redirect to login page after logout


class ProfileView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        account = get_object_or_404(CustomUser, pk=request.user.pk)
        form = UserProfileUpdateForm(instance=account)
        context = {
            "account": account,
            "form": form
        }
        return render(request, 'profile.html', context)

    def post(self, request, *args, **kwargs):
        account = get_object_or_404(CustomUser, pk=request.user.pk)

        # Ensure the current user is updating their own profile
        if request.user.pk != account.pk:
            return redirect('home')

        form = UserProfileUpdateForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile has been updated successfully")
            return redirect('profile')
        else:
            print(form.errors)

        context = {
            "account": account,
            "form": form
        }
        return render(request, 'profile.html', context)
