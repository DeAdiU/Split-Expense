from .models import User, Expense, ExpenseSplit
from django.contrib import admin
# Register your models here.

admin.site.register(User)
admin.site.register(Expense)
admin.site.register(ExpenseSplit)
