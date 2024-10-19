from rest_framework import serializers
from .models import User,Expense, ExpenseSplit


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'name']

    def validate(self, data):
        if '@' not in data['email']:
            raise serializers.ValidationError('Not a valid email id')
        try:
            validate_password(data['password'])
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return data

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password'])
        user.save()
        return user

class RepresentativeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name']
        
class ExpenseSplitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseSplit
        fields = ['user', 'amount_owed', 'split_type', 'percentage']

class ExpenseSerializer(serializers.ModelSerializer):
    splits = ExpenseSplitSerializer(many=True)

    class Meta:
        model = Expense
        fields = ['id', 'user', 'amount', 'description', 'created_at', 'splits']

    def create(self, validated_data):
        splits_data = validated_data.pop('splits')
        expense = Expense.objects.create(**validated_data)
        for split_data in splits_data:
            ExpenseSplit.objects.create(expense=expense, **split_data)
        return expense
