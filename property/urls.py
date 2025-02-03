from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf import settings

from django.contrib.auth import views as auth_views
from .views import *
from .views import (
    PropertyCreateView,
    PropertyListView,
    PropertyUpdateView,
    PropertyDeleteView,
)


urlpatterns = [
    path('', views.index, name='index'),                # Home page
    path('about/', views.about, name='about'),          # About page
    path('contact/', views.contact, name='contact'),    # Contact page
    path('agents/', views.agents, name='agents'),       # Agents listing page
    path('agent/<int:id>/', views.agent_single, name='agent_single'), # Single agent profile
    path('property_grid/', views.property_grid, name='property_grid'),   # Properties listing page
    path('property/<int:property_id>/', views.property_single, name='property_single'), # Single property detail
    path('property/edit/<int:property_id>/', views.property_edit, name='property_edit'),
    path('property/delete/<int:property_id>/', views.property_delete, name='property_delete'),
    path('blog/', views.blog_grid, name='blog_grid'),   # Blog listing page
    path('blog/<int:id>/', views.blog_single, name='blog_single'),   # Single blog post
    path('sign-in/', views.sign_in, name='sign_in'),
    path('sign-up/', views.sign_up, name='sign_up'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('landlord_dashboard/', views.landlord_dashboard, name='landlord_dashboard'),
    path('tenant_dashboard/', views.tenant_dashboard, name='tenant_dashboard'),
    path('add_property/', add_property, name='add_property'), 
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('logout/', views.custom_logout, name='logout'),
    path('send_message/', views.send_message, name='send_message'), 
    path('property-search/', views.property_search, name='property_search'),  # URL for the search form
    path('property-search-results/', views.property_search_results, name='property_search_results'),  # URL for displaying results
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset_form.html'), name='password_reset'),     
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),     
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),     
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),

    # API Endpoints
    path('properties/', PropertyCreateView.as_view(), name='property-create'), # API endpoint for creating properties
    path('properties/list/', PropertyListView.as_view(), name='property-list'),         # List all properties
    path('properties/<int:pk>/', PropertyUpdateView.as_view(), name='property-update'), # Update a property
    path('properties/<int:pk>/delete/', PropertyDeleteView.as_view(), name='property-delete'), # Delete a property
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),  # URL for user login
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # URL for token refresh
]
