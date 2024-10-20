from rest_framework import serializers
from .models import User,Expense, ExpenseSplit
from decimal import Decimal
from django.contrib.auth.password_validation import validate_password

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'name', 'mobile_number']
        extra_kwargs = {
            'password': {'write_only': True}  
        }
    def validate(self, data):
        if '@' not in data['email']:
            raise serializers.ValidationError('Not a valid email id')
        try:
            validate_password(data['password'])
        except serializers.ValidationError as e:
            raise serializers.ValidationError(e.messages)
        
        return data

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            name=validated_data['name'],
            mobile_number=validated_data['mobile_number']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
class RepresentativeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'mobile_number']
        
class ExpenseSplitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseSplit
        fields = ['user', 'amount_owed', 'split_type', 'percentage']

class ExpenseSplitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseSplit
        fields = ['user', 'amount_owed', 'split_type', 'percentage']

class ExpenseSerializer(serializers.ModelSerializer):
    splits = ExpenseSplitSerializer(many=True)

    class Meta:
        model = Expense
        fields = ['id', 'user', 'amount', 'description', 'created_at', 'splits']

    def validate(self, data):
        amount = data['amount']
        splits = data['splits']
        total_amount = Decimal(0)
        total_percentage = Decimal(0)
        split_type = None

        for split in splits:
            if split_type is None:
                split_type = split['split_type']  # Set the split type based on the first entry
            elif split['split_type'] != split_type:
                raise serializers.ValidationError("All Splits do not have same Split type.")

            if split['split_type'] == 'exact':
                total_amount += split['amount_owed']
            elif split['split_type'] == 'equal':
                total_amount += split['amount_owed']
            elif split['split_type'] == 'percentage':
                if split['percentage'] is None:
                    raise serializers.ValidationError("Percentage Value must be provided")
                total_percentage += split['percentage']

        # Validate exact splits sum
        if split_type == 'exact' and total_amount != amount:
            raise serializers.ValidationError(f"Total amount for 'exact' split is not equal the expense amount ({amount}).")

        # Validate equal splits
        if split_type == 'equal':
            expected_amount = amount / len(splits)
            for split in splits:
                if split['amount_owed'] != expected_amount:
                    raise serializers.ValidationError(f"Each split must be equal to {expected_amount} for 'equal' split type.")

        # Validate percentage splits sum
        if split_type == 'percentage' and total_percentage != 100:
            raise serializers.ValidationError(f"Total percentage for 'percentage' split must equal 100% (currently {total_percentage}%).")

        return data

    def create(self, validated_data):
        
        splits_data = validated_data.pop('splits')
        expense = Expense.objects.create(**validated_data)

        for split_data in splits_data:
            ExpenseSplit.objects.create(expense=expense, **split_data)

        return expense