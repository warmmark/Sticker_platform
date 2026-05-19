from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Listing, Message, Order, Profile


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'nickname', 'about', 'telegram_url', 'vk_url', 'instagram_url', 'portfolio_url']


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'category', 'description', 'price', 'deadline_days', 'preview_image', 'is_active']


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['comment']
        widgets = {'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Опишите, что именно нужно сделать'})}


class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['text']
        widgets = {'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Введите сообщение'})}
