import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from django.db import models
from django.conf import settings
from .enums import SplitType  

# Create your models here.


class User(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=10)
    password = models.CharField(max_length=128)
    date_joined = models.DateTimeField(default=timezone.now)

    def set_password(self, raw_password):
        #hashing password
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        #checking password
        return check_password(raw_password, self.password)

    def __str__(self):
        return f"{self.id} - {self.email}"

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.description} - {self.amount}"

class ExpenseSplit(models.Model):
    expense = models.ForeignKey(Expense, related_name='splits', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount_owed = models.DecimalField(max_digits=10, decimal_places=2)
    split_type = models.CharField(
        max_length=20,
        choices=[(split_type.value, split_type.name.capitalize()) for split_type in SplitType]
    )
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Used only for percentage splits

    def __str__(self):
        return f"{self.user.email} owes {self.amount_owed} for {self.expense.description} ({self.split_type})"

