from django.contrib import admin
from django.conf.urls import include
from .views import (SignupView, LoginView, user_expenses, create_expense, 
                    user_balance_view,  OverallExpensesView, 
                    download_balance_sheet)
from django.urls import path, re_path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# DRF-YASG schema view for Swagger API documentation
schema_view = get_schema_view(
   openapi.Info(
      title="Expense Sharing API",  # API title
      default_version='v1',  # API version
      description="API documentation for the Expense Sharing Application",  # API description
      contact=openapi.Contact(email="adityauttarwar29@gmail.com"),  # Support email for the API
      
   ),
   public=True,  # Public visibility
)

# URL patterns for API endpoints
urlpatterns = [
    path('register/', SignupView.as_view(), name='register'),  # User registration
    path('login/', LoginView.as_view(), name='login'),  # User login
    path('expenses/', user_expenses, name='expenses'),  # Fetch expenses of the authenticated user
    path('create_expense/', create_expense, name='create_expense'),  # Create a new expense
    path('balance/', user_balance_view, name='balance'),  # Get balance overview for the user
   #  path('expenses/user/', UserExpensesView, name='user-expenses'),  # List expenses for a specific user
    path('expenses/overall/', OverallExpensesView.as_view(), name='overall-expenses'),  # List overall expenses for all users
    path('expenses/balance-sheet/', download_balance_sheet, name='download-balance-sheet'),  # Download balance sheet
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),  # Swagger UI for API documentation
]
