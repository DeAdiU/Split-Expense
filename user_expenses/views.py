from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,generics
from .serializers import UserSerializer, RepresentativeSerializer, ExpenseSerializer
from .models import User, Expense, ExpenseSplit
import datetime
import jwt  
from django.conf import settings
from rest_framework.decorators import api_view
from django.db.models import Sum
import csv
from django.http import HttpResponse
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema

# Create your views here.

class SignupView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = generate_jwt_token(user)
            return Response({'token': token}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        try:
            user = User.objects.get(email=email)
            serializer = UserSerializer(user)
            if user.check_password(password):
                token = generate_jwt_token(user)
                return Response({'token': token, 'user':serializer.data}, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid password'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def get_user_from_token(request):
    token = request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
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


def generate_jwt_token(user):
    payload = {
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        'iat': datetime.datetime.utcnow()
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token


@api_view(['GET'])
def user_expenses(request):
    user = get_user_from_token(request)

    if user is None:  # Check if the user is None, indicating an error occurred
        return Response({'error': 'Invalid token or user not found'}, status=status.HTTP_401_UNAUTHORIZED)

    serializer = RepresentativeSerializer(user) 
    return Response({
        'user': serializer.data,
    }, status=status.HTTP_200_OK)

@swagger_auto_schema(methods=['post'], operation_description="Create an Expense")
@api_view(['POST'])
def create_expense(request):
    user = get_user_from_token(request)

    if user is None:  # Check if the user is None, indicating an error occurred
        return Response({'error': 'Invalid token or user not found'}, status=status.HTTP_401_UNAUTHORIZED)

    serializer = ExpenseSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(methods=['get'], operation_description="Retrieve User Expenses")
@api_view(['GET'])
def user_balance_view(request):
    user = get_user_from_token(request).get('id')
    # Owes to other users
    owes_to = (
        ExpenseSplit.objects.filter(user=user)
        .exclude(expense__user=user)
        .values('expense__user')
        .annotate(total_owed=Sum('amount_owed'))
        .order_by('-total_owed')
    )

    # Owed by other users
    owed_from = (
        ExpenseSplit.objects.filter(expense__user=user)
        .exclude(user=user)
        .values('user')
        .annotate(total_owed=Sum('amount_owed'))
        .order_by('-total_owed')
    )

    # Format the response
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

class UserExpensesView(generics.ListAPIView):
    serializer_class = ExpenseSerializer

    def get_queryset(self):
        user = get_user_from_token(self.request).get('id')  # Authenticated user
        return Expense.objects.filter(user=user)
    
    def get(self, request, *args, **kwargs):
        expenses = self.get_queryset()
        serializer = self.get_serializer(expenses, many=True)
        return JsonResponse(serializer.data, safe=False)

class OverallExpensesView(generics.ListAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

    def get(self, request, *args, **kwargs):
        expenses = self.get_queryset()
        serializer = self.get_serializer(expenses, many=True)
        return JsonResponse(serializer.data, safe=False)


def download_balance_sheet(request):
    user = get_user_from_token(request)
    user_id = user.get('id')
    splits = ExpenseSplit.objects.filter(user=user_id)

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="balance_sheet_{user.get('name')}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Expense', 'Amount Owed', 'Split Type', 'Percentage', 'Date'])

    for split in splits:
        writer.writerow([
            split.expense.description,
            split.amount_owed,
            split.split_type,
            split.percentage if split.split_type == 'percentage' else 'N/A',
            split.expense.created_at
        ])

    return response