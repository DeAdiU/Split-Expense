from django.contrib import admin
from django.conf.urls import include
from .views import SignupView,LoginView, user_expenses, create_expense, user_balance_view, UserExpensesView, OverallExpensesView, download_balance_sheet
from django.urls import path, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Expense Sharing API",
      default_version='v1',
      description="API documentation for the Expense Sharing Application",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="support@example.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
)

urlpatterns = [
    path('register/',SignupView.as_view(),name='register'),
    path('login/',LoginView.as_view(),name='login'),
    path('expenses/',user_expenses,name='expenses'),
    path('create_expense/',create_expense,name='create_expense'),
    path('balance/',user_balance_view,name='balance'),
    path('expenses/user/', UserExpensesView.as_view(), name='user-expenses'),
    path('expenses/overall/', OverallExpensesView.as_view(), name='overall-expenses'),
    path('expenses/balance-sheet/', download_balance_sheet, name='download-balance-sheet'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

]
