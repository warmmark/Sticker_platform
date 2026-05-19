from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('listing/<int:pk>/', views.listing_detail, name='listing_detail'),
    path('listing/<int:pk>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('listing/<int:pk>/order/', views.create_order, name='create_order'),
    path('listing/<int:pk>/message/', views.start_conversation, name='start_conversation'),

    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='marketplace/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('profile/', views.profile, name='profile'),
    path('my-listings/', views.my_listings, name='my_listings'),
    path('my-listings/create/', views.listing_create, name='listing_create'),
    path('my-listings/<int:pk>/edit/', views.listing_update, name='listing_update'),
    path('my-listings/<int:pk>/delete/', views.listing_delete, name='listing_delete'),

    path('favorites/', views.favorites, name='favorites'),
    path('orders/', views.orders, name='orders'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),

    path('messages/', views.conversations, name='conversations'),
    path('messages/<int:pk>/', views.conversation_detail, name='conversation_detail'),
]
