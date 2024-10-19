from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from .views import SignupView,LoginView, user_expenses, ExpenseCreateView, UserExpensesView

urlpatterns = [
    path('register/',SignupView.as_view(),name='register'),
    path('login/',LoginView.as_view(),name='login'),
    path('expenses/',user_expenses,name='expenses'),
    path('expenses/', ExpenseCreateView.as_view(), name='expense-create'),
    path('user-expenses/', UserExpensesView.as_view(), name='user-expenses'),

]
