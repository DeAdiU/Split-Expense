from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from .serializers import UserSerializer, RepresentativeSerializer, LoginSerializer, ExpenseSerializer
from .models import User, Expense, ExpenseSplit
import datetime
import jwt  
from django.conf import settings
from rest_framework.decorators import api_view
from django.db.models import Sum
import csv
from django.http import HttpResponse, JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers

# Views for the expense-sharing application

# Signup view for user registration
class SignupView(APIView):
    @swagger_auto_schema(request_body=UserSerializer,
    responses={200: "User created successfully", 400: "Invalid credentials or errors"})
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = generate_jwt_token(user)
            return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Serializer for login
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()  # User's email
    password = serializers.CharField()  # User's password

# Login view for user authentication
class LoginView(APIView):
    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={200: "User logged in successfully", 400: "Invalid credentials or errors"}
    )
    def post(self, request):
        # Use serializer to validate request data
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            try:
                user = User.objects.get(email=email)
                user_serializer = UserSerializer(user)
                if user.check_password(password):
                    token = generate_jwt_token(user)
                    return Response({'token': token, 'user': user_serializer.data}, status=status.HTTP_200_OK)
                return Response({'error': 'Invalid password'}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({'error': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Function to decode JWT and retrieve user information
def get_user_from_token(request):
    token = request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')

    if not token:
        return Response({'error': 'Missing token'}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user = User.objects.get(id=payload['user_id'])
        serializer = UserSerializer(user)
        return serializer.data
    except jwt.ExpiredSignatureError:
        return Response({'error': 'Signature expired'}, status=status.HTTP_401_UNAUTHORIZED)
    except jwt.DecodeError:
        return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Function to generate JWT token for a user
def generate_jwt_token(user):
    payload = {
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        'iat': datetime.datetime.utcnow()
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token

# View to fetch user's expenses
@api_view(['GET'])
def user_expenses(request):
    user = get_user_from_token(request)

    if isinstance(user, Response):
        return user
    serializer = RepresentativeSerializer(user) 
    return Response({
        'user': serializer.data,
    }, status=status.HTTP_200_OK)

# View to create a new expense
@swagger_auto_schema(methods=['post'], operation_description="Create an Expense", 
request_body=ExpenseSerializer, responses={201: "Expense created successfully", 400: "(Bad Request): Raised when the input validation fails (e.g., missing or invalid fields)."})
@api_view(['POST'])
def create_expense(request):
    user = get_user_from_token(request)
    if isinstance(user, Response):
        return user

    user = user.get('id')
    serializer = ExpenseSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# View to retrieve user's balance with other users
@swagger_auto_schema(methods=['get'], operation_description="Retrieve User Balance"
,responses={200: "User balance retrieved successfully", 401 : "(Unauthorized): Raised when the token is invalid, missing, or expired.",
404 : "(Not Found): Raised when the requested resource (like a user or expense) cannot be found.", 400: "(Bad Request): Raised when the input validation fails (e.g., missing or invalid fields)."})
@api_view(['GET'])
def user_balance_view(request):
    user = get_user_from_token(request)
    if isinstance(user, Response):
        return user

    user = user.get('id')
    
    # Get amounts the user owes to others
    owes_to = (
        ExpenseSplit.objects.filter(user=user)
        .exclude(expense__user=user)
        .values('expense__user')
        .annotate(total_owed=Sum('amount_owed'))
        .order_by('-total_owed')
    )

    # Get amounts owed to the user by others
    owed_from = (
        ExpenseSplit.objects.filter(expense__user=user)
        .exclude(user=user)
        .values('user')
        .annotate(total_owed=Sum('amount_owed'))
        .order_by('-total_owed')
    )

    # Format the response data
    owes_to_data = [
        {
            'to_user': User.objects.get(pk=item['expense__user']).name,
            'total_owed': item['total_owed']
        }
        for item in owes_to
    ]

    owed_from_data = [
        {
            'from_user': User.objects.get(pk=item['user']).name,
            'total_owed': item['total_owed']
        }
        for item in owed_from
    ]

    return Response({
        'owes_to': owes_to_data,
        'owed_from': owed_from_data
    })


# View to list overall expenses for all users
class OverallExpensesView(generics.ListAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

    def get(self, request, *args, **kwargs):
        expenses = self.get_queryset()
        serializer = self.get_serializer(expenses, many=True)
        return JsonResponse(serializer.data, safe=False)

# View to download the balance sheet as a CSV
def download_balance_sheet(request):
    
    user = get_user_from_token(request)
    if isinstance(user, Response):
        return user
    user_id = user.get('id')
    
    splits = ExpenseSplit.objects.filter(user=user_id)

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="balance_sheet_{user.get('name')}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Expense', 'Amount Owed', 'Split Type', 'Percentage', 'Date', 'Owed To/From'])

    for split in splits:
        if split.expense.user == user_id:
            owed_to_from = f'owed from {split.user.name}'
        else:
            owed_to_from = f'owed to {split.expense.user.name}'
        writer.writerow([
            split.expense.description,
            split.amount_owed,
            split.split_type,
            split.percentage if split.split_type == 'percentage' else 'N/A',
            split.expense.created_at,
            owed_to_from
        ])

    return response

